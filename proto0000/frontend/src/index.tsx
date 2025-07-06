/*
 * -------------------------------------------------
 * ・ファイル名：index.tsx
 * ・ファイル内容：React アプリケーションのエントリーポイント
 * ・作成日時：2025/07/06 17:56:00  Claude Code
 * -------------------------------------------------
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);