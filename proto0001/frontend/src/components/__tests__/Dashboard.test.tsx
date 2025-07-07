/*
 * -------------------------------------------------
 * ・ファイル名：Dashboard.test.tsx
 * ・ファイル内容：ダッシュボードコンポーネントの単体テスト
 * ・作成日時：2025/07/06 17:56:00  Claude Code
 * -------------------------------------------------
 * -------------------------------------------------
 * ・更新日時：2025/07/07 12:01:00  更新者：Claude Code
 * ・更新内容：axiosモックの修正とチャット機能テスト追加
 * -------------------------------------------------
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../Dashboard';
import { AuthProvider } from '../../contexts/AuthContext';

// axiosのモック
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

const MockedDashboard = () => (
  <BrowserRouter>
    <AuthProvider>
      <Dashboard />
    </AuthProvider>
  </BrowserRouter>
);

describe('Dashboard Component', () => {
  beforeEach(() => {
    mockedAxios.get.mockResolvedValue({
      data: {
        message: 'こんにちは、testAIさん！',
        dashboard_data: {
          total_users: 1,
          login_time: '2025/07/06 17:56:00'
        }
      }
    });
  });

  test('ダッシュボードが正しく表示される', async () => {
    render(<MockedDashboard />);
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'ダッシュボード' })).toBeInTheDocument();
    });
  });

  test('ログアウトボタンが表示される', async () => {
    render(<MockedDashboard />);
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'ログアウト' })).toBeInTheDocument();
    });
  });

  test('ダッシュボードデータが正しく表示される', async () => {
    render(<MockedDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('こんにちは、testAIさん！')).toBeInTheDocument();
      expect(screen.getByText('総ユーザー数: 1')).toBeInTheDocument();
    });
  });

  test('APIエラー時にエラーメッセージが表示される', async () => {
    mockedAxios.get.mockRejectedValue(new Error('API Error'));
    
    render(<MockedDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('ダッシュボードデータの取得に失敗しました')).toBeInTheDocument();
    });
  });

  test('AIチャットボタンが表示される', async () => {
    render(<MockedDashboard />);
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'AIチャットを開始' })).toBeInTheDocument();
    });
  });

  test('AIチャットボタンクリックでチャット画面に遷移する', async () => {
    render(<MockedDashboard />);
    
    await waitFor(() => {
      const chatButton = screen.getByRole('button', { name: 'AIチャットを開始' });
      fireEvent.click(chatButton);
    });

    // チャット画面の要素が表示されることを確認
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'AIチャット' })).toBeInTheDocument();
    });
  });
});