/*
 * -------------------------------------------------
 * ・ファイル名：Dashboard.tsx
 * ・ファイル内容：ダッシュボード画面コンポーネント
 * ・作成日時：2025/07/06 17:56:00  Claude Code
 * -------------------------------------------------
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

interface DashboardData {
  message: string;
  dashboard_data: {
    total_users: number;
    login_time: string;
  };
}

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await axios.get<DashboardData>('http://localhost:8000/dashboard');
        setDashboardData(response.data);
      } catch (error) {
        console.error('ダッシュボードデータの取得エラー:', error);
        setError('ダッシュボードデータの取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleLogout = () => {
    logout();
  };

  if (loading) {
    return <div className="loading">読み込み中...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>ダッシュボード</h1>
        <button onClick={handleLogout} className="logout-button">
          ログアウト
        </button>
      </div>
      
      <div className="dashboard-content">
        <div className="dashboard-card">
          <h2>ようこそ！</h2>
          <p>{dashboardData?.message}</p>
          <p>ログイン時刻: {dashboardData?.dashboard_data.login_time}</p>
        </div>
        
        <div className="dashboard-card">
          <h2>システム情報</h2>
          <p>総ユーザー数: {dashboardData?.dashboard_data.total_users}</p>
          <p>現在のユーザー: {user}</p>
        </div>
        
        <div className="dashboard-card">
          <h2>機能メニュー</h2>
          <p>このダッシュボードでは、以下の機能をご利用いただけます：</p>
          <ul>
            <li>ユーザー情報の確認</li>
            <li>システム状態の監視</li>
            <li>各種設定の変更</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;