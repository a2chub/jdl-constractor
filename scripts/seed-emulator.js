const { initializeApp } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');

// Firebase Adminの初期化
console.log('Initializing Firebase Admin...');
initializeApp({ 
  projectId: 'jdl-constructor-local'
});

const db = getFirestore();

// エミュレーターに接続
console.log('Connecting to Firestore emulator...');
db.settings({
  host: 'localhost:8081',  // 正しいポート番号に修正
  ssl: false
});

// サンプルデータ
const sampleData = {
  teams: [
    {
      id: 'team1',
      name: 'サンプルチーム1',
      description: 'テスト用チーム1です',
      members: ['user1', 'user2'],
      createdAt: new Date(),
      updatedAt: new Date()
    },
    {
      id: 'team2',
      name: 'サンプルチーム2',
      description: 'テスト用チーム2です',
      members: ['user3', 'user4'],
      createdAt: new Date(),
      updatedAt: new Date()
    }
  ],
  users: [
    {
      id: 'user1',
      name: 'テストユーザー1',
      email: 'test1@example.com',
      role: 'admin',
      createdAt: new Date(),
      updatedAt: new Date()
    },
    {
      id: 'user2',
      name: 'テストユーザー2',
      email: 'test2@example.com',
      role: 'member',
      createdAt: new Date(),
      updatedAt: new Date()
    }
  ]
};

// 接続テスト
async function testConnection() {
  try {
    console.log('Testing Firestore connection...');
    const testDoc = await db.collection('_test').doc('connection').set({
      timestamp: new Date()
    });
    await db.collection('_test').doc('connection').delete();
    console.log('Firestore connection successful!');
    return true;
  } catch (error) {
    console.error('Firestore connection failed:', error);
    return false;
  }
}

// データの投入
async function seedData() {
  try {
    // 接続テスト
    const isConnected = await testConnection();
    if (!isConnected) {
      console.error('Unable to connect to Firestore emulator. Please check if the emulator is running on port 8081.');
      process.exit(1);
    }

    console.log('Starting data seeding...');

    // チームデータの投入
    for (const team of sampleData.teams) {
      await db.collection('teams').doc(team.id).set(team);
      console.log(`Team created: ${team.name}`);
    }

    // ユーザーデータの投入
    for (const user of sampleData.users) {
      await db.collection('users').doc(user.id).set(user);
      console.log(`User created: ${user.name}`);
    }

    console.log('Seed data successfully loaded!');
    process.exit(0);
  } catch (error) {
    console.error('Error seeding data:', error.stack);
    process.exit(1);
  }
}

// メイン処理
console.log('Starting seed process...');
seedData(); 