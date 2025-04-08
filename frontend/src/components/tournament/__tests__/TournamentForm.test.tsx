import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TournamentForm } from '../TournamentForm';
import { BrowserRouter } from 'react-router-dom'; // For useNavigate mock
import { I18nextProvider } from 'react-i18next';
import i18n from '../../../i18n-test-config.ts'; // Add .ts extension

// Mock dependencies
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const original = await vi.importActual('react-router-dom');
  return {
    ...original,
    useNavigate: () => mockNavigate,
  };
});

// useAuth フックをモック
vi.mock('../../hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({ 
    user: { 
      uid: 'test-admin-user-id', 
      // Mock other user properties if needed by the component
      getIdToken: async () => 'mock-id-token' // Mock getIdToken if used indirectly
    }, 
    isAdmin: true, // Assume admin for form rendering/submission tests
    loading: false, 
    error: null 
  })),
}));

const mockOnSubmit = vi.fn();

const renderComponent = (props = {}) => {
  const defaultProps = {
    onSubmit: mockOnSubmit,
    ...props,
  };
  return render(
    <BrowserRouter>
      <I18nextProvider i18n={i18n}>
        <TournamentForm {...defaultProps} />
      </I18nextProvider>
    </BrowserRouter>
  );
};

describe('TournamentForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockOnSubmit.mockResolvedValue(undefined); // Default to successful submit
  });

  it('renders create form correctly', () => {
    renderComponent();
    expect(screen.getByRole('heading', { name: /トーナメントを作成/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/トーナメント名/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/説明/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/開催場所/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/参加費/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/開始日時/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/終了日時/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/エントリー開始日時/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/エントリー終了日時/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/ステータス/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /作成/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /キャンセル/i })).toBeInTheDocument();
  });

  it('renders edit form correctly with initial data', () => {
    const initialData = {
      name: 'Existing Tournament',
      description: 'Existing Desc',
      venue: 'Existing Venue',
      entry_fee: 1000,
      start_date: '2025-10-01T10:00',
      end_date: '2025-10-02T18:00',
      entry_start_date: '2025-09-01T10:00',
      entry_end_date: '2025-09-15T18:00',
      status: 'entry_open' as const,
    };
    renderComponent({ tournamentId: 't1', initialData });

    expect(screen.getByRole('heading', { name: /トーナメントを編集/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/トーナメント名/i)).toHaveValue('Existing Tournament');
    expect(screen.getByLabelText(/説明/i)).toHaveValue('Existing Desc');
    expect(screen.getByLabelText(/開催場所/i)).toHaveValue('Existing Venue');
    expect(screen.getByLabelText(/参加費/i)).toHaveValue(1000);
    // Note: datetime-local input values are tricky to assert directly in jsdom
    expect(screen.getByLabelText(/ステータス/i)).toHaveValue('entry_open');
    expect(screen.getByRole('button', { name: /更新/i })).toBeInTheDocument();
  });

  it('shows validation error for required fields', async () => {
    renderComponent();
    const user = userEvent.setup();
    const submitButton = screen.getByRole('button', { name: /作成/i });

    await user.click(submitButton);

    expect(await screen.findByText(/トーナメント名は必須です/i)).toBeInTheDocument();
    expect(screen.getByText(/開催場所は必須です/i)).toBeInTheDocument();
    expect(screen.getByText(/開始日時は必須です/i)).toBeInTheDocument();
    // Add checks for other required date fields
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('shows validation error for invalid date range (end before start)', async () => {
    renderComponent();
    const user = userEvent.setup();
    const startDateInput = screen.getByLabelText(/開始日時/i);
    const endDateInput = screen.getByLabelText(/終了日時/i);
    const submitButton = screen.getByRole('button', { name: /作成/i });

    // Fill required fields first
    await user.type(screen.getByLabelText(/トーナメント名/i), 'Test Name');
    await user.type(screen.getByLabelText(/開催場所/i), 'Test Venue');
    await user.type(screen.getByLabelText(/エントリー開始日時/i), '2025-01-01T10:00');
    await user.type(screen.getByLabelText(/エントリー終了日時/i), '2025-01-10T10:00');

    // Set invalid dates
    await user.type(startDateInput, '2025-10-02T10:00');
    await user.type(endDateInput, '2025-10-01T10:00'); // End date before start date

    await user.click(submitButton);

    expect(await screen.findByText(/終了日時は開始日時より後に設定してください/i)).toBeInTheDocument();
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('calls onSubmit with correct data on successful submission', async () => {
    renderComponent();
    const user = userEvent.setup();

    const formData = {
      name: 'Valid Tournament',
      description: 'Valid Desc',
      venue: 'Valid Venue',
      entry_fee: 500,
      start_date: '2025-11-01T10:00',
      end_date: '2025-11-02T18:00',
      entry_start_date: '2025-10-01T10:00',
      entry_end_date: '2025-10-15T18:00',
      status: 'draft' as const,
    };

    await user.type(screen.getByLabelText(/トーナメント名/i), formData.name);
    await user.type(screen.getByLabelText(/説明/i), formData.description);
    await user.type(screen.getByLabelText(/開催場所/i), formData.venue);
    // Use fireEvent for number input as userEvent.type might cause issues
    fireEvent.change(screen.getByLabelText(/参加費/i), { target: { value: formData.entry_fee.toString() } });
    await user.type(screen.getByLabelText(/開始日時/i), formData.start_date);
    await user.type(screen.getByLabelText(/終了日時/i), formData.end_date);
    await user.type(screen.getByLabelText(/エントリー開始日時/i), formData.entry_start_date);
    await user.type(screen.getByLabelText(/エントリー終了日時/i), formData.entry_end_date);
    // Status defaults to draft

    await user.click(screen.getByRole('button', { name: /作成/i }));

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledTimes(1);
      expect(mockOnSubmit).toHaveBeenCalledWith(formData);
    });
    // Check for navigation after successful submit
    await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/tournaments');
    });
  });

  it('shows error message when onSubmit throws an error', async () => {
    const apiError = 'サーバーエラーが発生しました';
    mockOnSubmit.mockRejectedValue(new Error(apiError)); // Simulate API error
    renderComponent();
    const user = userEvent.setup();

     // Fill form with valid data (similar to the success test)
     const formData = {
        name: 'Valid Tournament',
        description: 'Valid Desc',
        venue: 'Valid Venue',
        entry_fee: 500,
        start_date: '2025-11-01T10:00',
        end_date: '2025-11-02T18:00',
        entry_start_date: '2025-10-01T10:00',
        entry_end_date: '2025-10-15T18:00',
        status: 'draft' as const,
      };
      await user.type(screen.getByLabelText(/トーナメント名/i), formData.name);
      await user.type(screen.getByLabelText(/開催場所/i), formData.venue);
      fireEvent.change(screen.getByLabelText(/参加費/i), { target: { value: formData.entry_fee.toString() } });
      await user.type(screen.getByLabelText(/開始日時/i), formData.start_date);
      await user.type(screen.getByLabelText(/終了日時/i), formData.end_date);
      await user.type(screen.getByLabelText(/エントリー開始日時/i), formData.entry_start_date);
      await user.type(screen.getByLabelText(/エントリー終了日時/i), formData.entry_end_date);

    await user.click(screen.getByRole('button', { name: /作成/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(apiError);
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  // Add more tests for:
  // - Other validation rules (entry end date vs start date, entry end date vs tournament start date)
  // - Status dropdown change
  // - Input field changes updating state
});

// Helper: Create a minimal i18n config for tests
// You might want to move this to a separate test setup file
// import i18n from 'i18next';
// import { initReactI18next } from 'react-i18next';
// import translationJA from '../../../locales/ja/tournament.json'; // Adjust path as needed

// i18n
//   .use(initReactI18next)
//   .init({
//     lng: 'ja',
//     fallbackLng: 'ja',
//     resources: {
//       ja: {
//         tournament: translationJA, // Use the correct namespace if needed
//       },
//     },
//     interpolation: {
//       escapeValue: false, // React already safes from xss
//     },
//   });

// export default i18n;
