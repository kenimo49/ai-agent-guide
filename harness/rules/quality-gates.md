# Quality Gates

## Pre-Publish Checks (全てPASSで公開)

### 必須チェック
- [ ] 文字数 >= 3,000
- [ ] キーワードがタイトルに含まれる
- [ ] キーワードがH2の1つ以上に含まれる
- [ ] メタディスクリプション: 80-160文字
- [ ] AI Slopスコア < 5%
- [ ] コードブロックが1つ以上
- [ ] 内部リンクが1つ以上

### 推奨チェック
- [ ] 画像/図が1つ以上
- [ ] 文字数 >= 4,000
- [ ] H2が4-6個

## AI Slop Threshold
- Slopパターンマッチ / 総文数 < 5%

## Rewrite Limits
- 1記事あたり最大2回
- 2回リライトしても改善しない場合はアーカイブ

## Performance Thresholds (GA4)
- 🟢 High: PV > 100/week AND duration > 120s
- 🟡 Normal: PV 20-100/week
- 🔴 Low: PV < 20/week OR duration < 30s OR bounce > 80%
