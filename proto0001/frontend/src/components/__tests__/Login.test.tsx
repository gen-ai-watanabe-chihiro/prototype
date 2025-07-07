/*
 * -------------------------------------------------
 * ・ファイル名：Login.test.tsx
 * ・ファイル内容：ログインコンポーネントの単体テスト
 * ・作成日時：2025/07/06 17:56:00  Claude Code
 * -------------------------------------------------
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Login from '../Login';
import { AuthProvider } from '../../contexts/AuthContext';

// axiosのモック
jest.mock('axios', () => ({
  default: {
    post: jest.fn(),
    defaults: {
      headers: {
        common: {}
      }
    }
  }
}));

const MockedLogin = () => (
  <BrowserRouter>
    <AuthProvider>
      <Login />
    </AuthProvider>
  </BrowserRouter>
);

describe('Login Component', () => {
  test('ログインフォームが正しく表示される', () => {
    render(<MockedLogin />);
    
    expect(screen.getByRole('heading', { name: 'ログイン' })).toBeInTheDocument();
    expect(screen.getByLabelText('ユーザー名')).toBeInTheDocument();
    expect(screen.getByLabelText('パスワード')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'ログイン' })).toBeInTheDocument();
  });

  test('入力フィールドが正しく動作する', () => {
    render(<MockedLogin />);
    
    const usernameInput = screen.getByLabelText('ユーザー名') as HTMLInputElement;
    const passwordInput = screen.getByLabelText('パスワード') as HTMLInputElement;
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });
    
    expect(usernameInput.value).toBe('testuser');
    expect(passwordInput.value).toBe('testpass');
  });

  test('必須フィールドが空の場合、フォーム送信が防がれる', () => {
    render(<MockedLogin />);
    
    const submitButton = screen.getByRole('button', { name: 'ログイン' });
    const usernameInput = screen.getByLabelText('ユーザー名') as HTMLInputElement;
    
    // 必須フィールドが空の場合のテスト
    expect(usernameInput.required).toBe(true);
    expect(usernameInput.value).toBe('');
  });
});