# Technical + Gameplay Integrity Checks

この文書は、LILIAのMVP前後に、設計正本、prompt、template、manual smokeが壊れていないかを確認するための横断チェック正本である。

`docs/RESUME_SMOKE_TEST.md` を置き換えない。
Resume Smoke Test は `new -> first scene -> save -> resume` の手動1周に集中し、この文書はそれを含む repo / session / prompt / gameplay の軽い整合確認を扱う。

## 1. Purpose

Technical + Gameplay Integrity Checks は、LILIAの設計正本、prompt、template、手動smokeが互いに矛盾せず、MVPで遊べる最小状態を保っているかを見るための横断Gateである。

目的は、重い自動テスト、AI Harness、大量ログ解析ではない。
初期MVPに必要な軽い整合確認として、`new -> first scene -> save -> resume` の体験が、event_card、voice、romance、growth update、story accumulation、crisis ability と矛盾なくつながるかを見る。

このチェックは、LILIAを壊すズレを早めに見つけるためのものだ。
チェック自体を、重い運用、CLI、launcher、production CIにしない。

## 2. Source Of Truth

- 中核思想: `docs/CORE_CONCEPT.md`
- state構造: `docs/STATE_STRUCTURE.md`
- new初期化: `docs/NEW_SESSION_INITIALIZATION.md`
- event_card可プレイ性: `docs/EVENT_CARD_PLAYABILITY.md`
- voice continuity: `docs/VOICE_CONTINUITY.md`
- romance / intimacy growth: `docs/ROMANCE_INTIMACY_GROWTH.md`
- resume smoke: `docs/RESUME_SMOKE_TEST.md`
- growth update: `docs/GROWTH_UPDATE_LOOP.md`
- story / relationship accumulation: `docs/STORY_RELATIONSHIP_ACCUMULATION.md`
- crisis / combat / ability constraint: `docs/CRISIS_COMBAT_ABILITY_CONSTRAINT_LOOP.md`
- prompt core: `prompt/core.md`
- new開始: `prompt/newgame.md`
- save / resume: `prompt/save_resume.md`
- session templates: `templates/session/`
- 手動チェックリスト: `tests/resume_smoke/manual_checklist.md`

`docs/RESUME_SMOKE_TEST.md` は、resume smoke の正本である。
この文書は、resume smoke を含む横断 integrity check の正本である。

## 3. Scope

初期MVPで見るもの:

- repo / docs / prompt / templates の必須ファイル存在。
- new初期化の最小state。
- event_card playability。
- voice continuity。
- romance / intimacy boundary。
- growth update。
- story accumulation。
- crisis / ability constraint。
- resume smoke。
- hotsetが正本化していないこと。
- memory / beliefs / unknown の分離。
- promptが肥大化していないこと。
- examplesが固定化していないこと。

初期MVPで見ないもの:

- AI Harness本実行。
- 大量ログ解析。
- 自動プレイ検証。
- launcher / CLI本実装。
- 画像 / 漫画 export。
- heavy combat engine。
- full plot検証。
- production CI。

## 4. Check Categories

### Repo / Docs Integrity

- `AGENTS.md` がある。
- `docs/ROADMAP.md` と `docs/HANDOFF.md` がある。
- 主要docsが存在する。
- ROADMAPのNext TaskとHANDOFFの次にやることが矛盾しない。
- 新規正本を追加した場合、ROADMAP / HANDOFF更新ルールに従う。

### Prompt Integrity

- `prompt/core.md` に `Example Anchoring Control` がある。
- `prompt/newgame.md` が必要な正本を参照している。
- `prompt/save_resume.md` がresume正本と必要な横断正本を参照している。
- 通常resumeで全部のstyle / referenceや重いdocsを必読にしていない。
- 例文が選択肢、固定台詞、固定設定になっていない。

### Template Integrity

- `templates/session/current/event_card.md` が visible problem / first concrete action / handles / relationship stake を持つ。
- `story_deck.md` が素材棚であり、現在sceneそのものやfull plotになっていない。
- `relationship_spine.md` が固定ルートではない。
- `state` / `memory` / `relationship` / `beliefs` / `voice` の責務が分かれている。
- `hotset` が正本ではなく再開用cacheとして扱われている。

### Gameplay Integrity

- event_cardが今触れる可視イベントになっている。
- voice continuityが巻き戻っていない。
- romance / intimacyが成人、合意、相互性、境界線、aftercareを守っている。
- growth updateが全ファイル更新ではなく、必要分だけ短く更新する。
- story accumulationがeventを関係の線へ変換している。
- crisis / abilityが万能解決や重い数値戦闘になっていない。

### Resume Smoke Integrity

- `docs/RESUME_SMOKE_TEST.md` と `tests/resume_smoke/manual_checklist.md` を使う。
- `new -> first scene -> save -> resume` の流れで確認する。
- resume 1ターン目で、声、距離感、event_card、relationship、memory、beliefsが戻るかを見る。
- hotsetだけで押し切らない。

## 5. Manual Checklist

手動チェックでは、最低限以下を見る。

- 必須docsがある。
- 必須promptがある。
- 必須templatesがある。
- event_cardが現在入口を持つ。
- story_deckとevent_cardの責務が分かれている。
- memoryは事実、beliefsはLILIA側仮説、unknownは未確定として分離されている。
- voice continuityが前回からつながる。
- romance / intimacyが境界線とaftercareを持つ。
- crisis / abilityが `can` / `cannot` / `cost` / `trace` / `risk` を持つ。
- resume smoke checklistが使える。

## 6. Minimal Script Policy

初期MVPではスクリプトは必須ではない。
作る場合も、以下の最小補助に限定する。

- ファイル存在確認。
- 見出し存在確認。
- ROADMAP / HANDOFF のNext Task簡易確認。
- templatesに必須見出しがあるか確認。
- promptに正本参照があるか確認。

禁止:

- AI Harness本実行。
- 大量ログ解析。
- 自動プレイ生成。
- launcher / CLI実装。
- 複雑なCI。
- gameplayの良し悪しを自動採点すること。

## 7. Gate Failure Conditions

以下のどれかに当てはまる場合、横断整合チェックは失敗している。

- ROADMAPとHANDOFFの現在地がズレている。
- 必須正本がない。
- promptが必要な正本を参照していない。
- event_cardが抽象的な違和感だけで、今触れる入口がない。
- story_deckがfull plotや巨大組織設定置き場になっている。
- hotsetが正本になっている。
- memoryに推測やunknownが混ざっている。
- beliefsでユーザーの内面を断定している。
- romance / intimacyが境界線やaftercareを失っている。
- crisis / abilityが万能解決や数値戦闘になっている。
- 通常resumeが重いdocsを全部読む設計になっている。
- AI Harnessや大量ログ解析が初期MVP必須になっている。

## 8. Gate Passing Conditions

以下を満たす場合、横断整合チェックは通過している。

- ROADMAP / HANDOFF / docs / prompt / templates の責務が分かれている。
- resume smokeが独立して使える。
- event_card / story_deck / relationship_spine の責務が分かれている。
- state / memory / relationship / beliefs / voice の保存責務が分かれている。
- `new -> first scene -> save -> resume` の確認観点がある。
- voice / romance / growth / story / crisis の各ループが手動チェックに反映されている。
- 初期MVPで重いAI Harnessや大量ログ解析を要求していない。

## 9. Relationship to Resume Smoke

`docs/RESUME_SMOKE_TEST.md` は、実際のresume手順と1ターン目の温度確認に集中する。

`docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md` は、resume smokeを含む横断整合性を扱う。

resume smokeの具体チェックは重複させない。
必要な場合は、`tests/resume_smoke/manual_checklist.md` に参照として短く追加する。

## 10. Not Adopted

- AI Harness本実行。
- 大量ログ解析。
- 自動プレイ検証。
- production CI。
- launcher / CLI実装。
- 重いprompt auditor。
- gameplay自動採点。
- 画像 / 漫画 export検証。
- full plot検証。
- heavy combat検証。

## 11. Reason

ここまで多くの正本とテンプレートが揃ったため、次は壊れていないかを見る必要がある。

ただし、初期MVPで重い自動検証を入れると開発が止まる。
まずは軽い手動チェックと、将来の最小スクリプト余地だけを正本化する。

`docs/RESUME_SMOKE_TEST.md` に全部を入れると、resume smokeの責務が太る。
そのため、`new -> first scene -> save -> resume` の手動1周はResume Smoke Testに残し、repo / session / prompt / gameplay の横断確認はこの文書へ分離する。
