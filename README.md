# aws-study-gate-questions

Chrome 拡張機能「Study Gate」が読み込む、AWS 認定試験の練習問題パックです。

- `clf/` … AWS Certified Cloud Practitioner (CLF-C02)
- `saa/` … AWS Certified Solutions Architect – Associate（準備中）

毎週日曜に、Claude の定期タスクが新しいパックを1つ追加します。
問題の形式とルールは [AUTHORING.md](AUTHORING.md)、検証は `python3 tools/validate.py` です。

問題は AI が作成し、AWS 公式ドキュメントとの照合を経ていますが、公式教材ではありません。
