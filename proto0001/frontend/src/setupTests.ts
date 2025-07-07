/*
 * -------------------------------------------------
 * ・ファイル名：setupTests.ts
 * ・ファイル内容：テストセットアップファイル
 * ・作成日時：2025/07/06 17:56:00  Claude Code
 * -------------------------------------------------
 */

import '@testing-library/jest-dom';

// axiosのモック設定
jest.mock('axios', () => ({
  default: {
    get: jest.fn(),
    post: jest.fn(),
    defaults: {
      headers: {
        common: {}
      }
    }
  }
}));