# LILIA Implementation History

この文書は、LILIAでこれまで実装・設計・検証された主要機能を棚卸しするトップレベル履歴である。

## 1. Purpose

LILIAの実装済み内容を把握し、今後の商用化WBSと重複開発を防ぐ。

## 2. Implemented Summary

- concept / growth basis
- save/resume 軽量読み順
- startup分岐
- state scaffold
- style reference scaffold
- Style Defaults / Intimacy Defaults Completion
- New Session Initialization
- character YAML → AI profile → spines → 13 downstream docs
- Event Card Playability Gate
- Voice Continuity Gate
- Growth Update Loop
- apply-turn MVP
- next_hook 導線
- autosave counter
- scene-tick MVP
- Story / Relationship Accumulation Loop
- story_spine / relationship_spine AI駆動化
- Story Reference Engine
- 5層 self-understanding 参照導線
- Deepening Tags 評価基準
- Crisis / Combat / Ability Constraint Loop docs
- Technical / Gameplay Integrity Checks docs
- MVP Playtest
- Full Loop Manual Smoke checklist
- 最小 launcher / CLI
- AI engine 接続
- Newgame Q&A Q1-Q9
- LILIA Persona Profile
- Engine Runner Refactor
- Auto-save Chain Closure
- Codex Rollout Logs Archive
- 文豪シーン
- Emotional Design Principles
- Hidden 深化ベクトル軸名修正
- lilia_name / lilia_display_name

## 3. Wave History

- Wave 1: 散文層・キャラ会議変換: done
- Wave 2: echo拡張・decision_index: done
- Wave 3: 50作品参考カタログ: done
- Wave 4: Structure / Pattern Reference Libraries: done
- Wave 5: story_spine導入: done
- Wave 6: Opening Scene & Heroine Appearance: done
- Wave 7: Newgame Q&A Refinement & Protagonist Profile: done
- Wave 8: Knowledge Boundary Management: done
- Wave 9: Root Cure: done
- Wave 10: Q&A Redesign: done
- Wave 10.1: Q3-Q5 Independence Restoration: done
- Wave 10.2: Main Question Template Flexibility: done
- Wave 10.3: Fallback Field Quality + Knowledge Boundary Meta HIDDEN: done
- Wave 10.4: Protagonist Inner Monologue Boundary: done
- Wave 11: AI-driven Story / Relationship Spine Generation: done
- Wave 12.1: AI-driven LILIA Persona Profile Generation: done
- Wave 12.2: AI-driven Downstream Session Documents: done
- Wave 13: Voice Continuity Gate Validator: done
- Wave 14: Event Card Playability Gate Validator: done
- Wave 15: Engine Runner Refactor: done
- Wave Y-F: Auto-save Chain Closure: done
- Wave Y-H: Codex Rollout Logs Archive: done

## 4. Known Remaining Technical Items

- Romance / Intimacy Growth Loop の実生成コード
- Resume Smoke Test の実生成コード
- Crisis / Combat / Ability Constraint Loop の実生成コード
- scene-tick 毎ターン実行と apply-turn 発火の実機目視確認
- 深化ベクトル 0-5 数値運用ロジック確定
- Voice Continuity Validator の hard fail 化判断
- 呼び方の厳密比較
- relationship 進行語彙リスト正本化
- decision_index と hotset の詳細マッチ
- core fixed と volatile の意味的矛盾検出

## 4.1 Pending Items（2026-05-07 整理、詳細は docs/ROADMAP.md 「保留事項」を正本）

- P-A. テンポ管理（何をどこまでどう出すか）: 1 ターン分量上限、描写濃度の段階分け、沈黙の扱い、場面転換頻度、通常ターン軽量化ルール。仮案あり、要確定。Wave Y-A の延長。Wave Y-B1 で症状一部改善のため優先度低
- P-B. Hidden 深化ベクトル運用: 6 軸（安心 / 欲情 / 共犯 / 生活 / 受容 / 摩耗）の 0-5 数値運用 vs 自然言語運用 vs ハイブリッドの選択
- P-C. 深化タグ機械チェック: inner-galge デフォルト 14 タグ + ヒロイン追加機構の解放条件自動評価
- P-D. 3 本フック運用（戦闘なし版）: 2026-05-07 にβ前P0へ格上げ。Main Hook / Relationship Hook / Life-Exploration Hook の3方向並列、Active Hook、story_deck保持、apply-turn更新、wanderer playtest を `RELEASE_WBS.md` の `HOOK-001〜HOOK-006` で管理する
- P-E. 世界移動・物語射程の境界（仮案）: 自然範囲 / 関係段階判定 / 射程外 / 世界観違反の 4 段階。Player Action Prompt 改修（Wave 17 候補）と合わせて確定する
- P-F. NPC 昇格（ヒロイン非昇格仕様）: 初期実装では NPC はヒロインに昇格しない。Tier 1〜4 の範囲だけ扱い、複数ヒロイン Wave で改めて昇格条件を設計
- P-G. 軽量 Integrity Audit Tool: `docs/INTEGRITY_AUDIT_20260505.md` の手動監査手順を `tools/audit/integrity_audit.py` として定型化

## 5. Commercialization Gap

- WebUI
- ユーザー管理
- 課金
- 画像生成
- 画像キャラ一貫性検証
- 商用利用規約
- β募集導線
- LP / マーケ素材
- 運用ログ / 障害対応
- AI Playtest Smoke
- Three Hook Spine MVP
