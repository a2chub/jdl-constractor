/**
 * チームフォームコンポーネント
 * 
 * このコンポーネントは以下の機能を提供します：
 * - チームの新規作成
 * - 既存チームの編集
 * - フォームバリデーション
 * - 画像アップロード
 * - エラー表示
 */

import { FC, useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { LoadingSpinner } from '../LoadingSpinner';
import { ErrorMessage } from '../ErrorMessage';
import { useAuth } from '../../hooks/useAuth';

interface TeamFormData {
  name: string;
  description: string;
  logo_url: string;
}

interface TeamFormProps {
  mode: 'create' | 'edit';
}

export const TeamForm: FC<TeamFormProps> = ({ mode }) => {
  const { teamId } = useParams<{ teamId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(mode === 'edit');
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<TeamFormData>({
    name: '',
    description: '',
    logo_url: '',
  });
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');

  useEffect(() => {
    const fetchTeamData = async () => {
      if (mode === 'edit' && teamId) {
        try {
          const response = await fetch(`/api/teams/${teamId}`);
          if (!response.ok) {
            throw new Error('チーム情報の取得に失敗しました');
          }
          const data = await response.json();
          setFormData({
            name: data.name,
            description: data.description,
            logo_url: data.logo_url,
          });
          setImagePreview(data.logo_url);
        } catch (err) {
          setError(err instanceof Error ? err.message : 'エラーが発生しました');
        } finally {
          setLoading(false);
        }
      }
    };

    fetchTeamData();
  }, [mode, teamId]);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 2 * 1024 * 1024) { // 2MB制限
        setError('画像サイズは2MB以下にしてください');
        return;
      }
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // 画像のアップロード（実際の実装ではCloud Storageなどを使用）
      let logo_url = formData.logo_url;
      if (imageFile) {
        // TODO: 画像アップロード処理の実装
        logo_url = '/path/to/uploaded/image.jpg';
      }

      const apiUrl = mode === 'create' ? '/api/teams' : `/api/teams/${teamId}`;
      const method = mode === 'create' ? 'POST' : 'PUT';

      const response = await fetch(apiUrl, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          logo_url,
        }),
      });

      if (!response.ok) {
        throw new Error('チームの保存に失敗しました');
      }

      const data = await response.json();
      navigate(`/teams/${data.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'エラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          {mode === 'create' ? 'チームを作成' : 'チーム情報を編集'}
        </h1>

        {error && <ErrorMessage message={error} className="mb-6" />}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium text-gray-700"
            >
              チーム名
            </label>
            <input
              type="text"
              id="name"
              required
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div>
            <label
              htmlFor="description"
              className="block text-sm font-medium text-gray-700"
            >
              説明
            </label>
            <textarea
              id="description"
              rows={4}
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div>
            <label
              htmlFor="logo"
              className="block text-sm font-medium text-gray-700"
            >
              ロゴ画像
            </label>
            <div className="mt-1 flex items-center space-x-4">
              <div className="w-24 h-24 relative">
                <img
                  src={imagePreview || '/default-team-logo.png'}
                  alt="チームロゴプレビュー"
                  className="w-full h-full object-cover rounded-lg"
                />
              </div>
              <input
                type="file"
                id="logo"
                accept="image/*"
                onChange={handleImageChange}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
            </div>
            <p className="mt-2 text-sm text-gray-500">
              2MB以下のJPG、PNG、GIF形式の画像をアップロードしてください
            </p>
          </div>

          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 font-medium py-2 px-6 rounded-md"
            >
              キャンセル
            </button>
            <button
              type="submit"
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-md"
            >
              {mode === 'create' ? '作成' : '更新'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}; 