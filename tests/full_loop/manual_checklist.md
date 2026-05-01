# LILIA Full Loop Manual Checklist

このチェックリストは、`new -> profile -> first scene -> Play Mode -> scene-tick -> apply-turn -> resume` を1本で確認するための手動smoke testです。
実session本文や `saves/` はgit管理しません。

## Scope

- 対象session: `test_full_loop_001`
- 確認対象: launcher / Codex interactive prompt / Persona Profile / Play Mode / autosave tick / Save Mode / resume
- 対象外: AI Harness、自動プレイ、大量ログ解析、画像/漫画export、production CI

## 1. New / Persona Profile / First Scene

1. `./lilia codex-new test_full_loop_001` を実行する。
2. Codex interactive が起動し、初期instructionが渡っていることを確認する。
3. Q1-Q7 に回答する。
4. Q&A完了後、first scene前に `saves/test_full_loop_001/lilia/main/profile.md` が生成されることを確認する。
5. `profile.md` が空テンプレートではなく、生活、行動、矛盾、反応、禁忌、everyday anchors を含む実内容になっていることを確認する。
6. `saves/test_full_loop_001/current/scene.md` が生成され、現在地、距離、見えているもの、行動余地が入っていることを確認する。
7. `saves/test_full_loop_001/current/event_card.md` が生成され、visible problem、first concrete action、handles、relationship stake、if ignored、next visible change が入っていることを確認する。
8. Codexが `first_scene_pending` で止まらず、first scene本文を出すことを確認する。

## 2. Play Mode

1. first scene後、通常プレイで2-3ターン進める。
2. ユーザー通常入力への返答で、LILIA / GMの本文が先に出ることを確認する。
3. 通常プレイ中に以下が出ないことを確認する。
   - `Edited files`
   - `git status`
   - `git diff`
   - `保存します`
   - `stateを更新します`
   - `session stateには保存済みです`
4. 通常プレイ中に `state.md`、`relationship.md`、`memory.md`、`beliefs.md`、`hotset.md` が勝手に更新されないことを確認する。

## 3. Scene Tick

1. 通常プレイ1ターン後の手動確認として、別terminalで `./lilia scene-tick test_full_loop_001` を実行する。
2. 出力が以下の形になることを確認する。

```text
scene tick: 1/10
autosave_required: false
```

3. `saves/test_full_loop_001/session.json` の `autosave.turns_since_save` が増えていることを確認する。
4. `scene-tick` によって `apply-turn` が自動実行されていないことを確認する。
5. 必要なら10回目まで `scene-tick` を実行し、`autosave_required: true` と保存提案だけが出ることを確認する。

## 4. Save Mode / Apply Turn

1. ユーザーが「保存して」と言った想定で、今回の2-3ターンから `turn_update.md` を作る。
2. 最小サンプルが必要な場合は `tests/apply_turn/sample_turn_update.md` を参照する。
3. 保存前の `profile.md` の更新時刻またはdiff対象を確認する。
4. `./lilia apply-turn test_full_loop_001 <turn_update.md>` を実行する。
5. 以下が更新されることを確認する。
   - `current/scene.md`
   - `lilia/main/state.md`
   - `current/relationship_overview.md`
   - `lilia/main/relationship.md`
   - `lilia/main/memory.md`
   - `lilia/main/beliefs.md`
   - `current/event_card.md`
   - `story/story_deck.md`
   - `story/relationship_spine.md`
   - `current/hotset.md`
   - `session.json`
6. `lilia/main/profile.md` が更新されていないことを確認する。
7. `current/hotset.md` が肥大化せず、次回1ターン用の短い要約になっていることを確認する。
8. `saves/test_full_loop_001/session.json` で autosave が以下へ戻ることを確認する。

```json
"autosave": {
  "enabled": true,
  "interval_turns": 10,
  "turns_since_save": 0,
  "autosave_required": false
}
```

## 5. Resume

1. `./lilia codex-resume test_full_loop_001` を実行する。
2. Codex interactive が起動し、resume用の初期instructionが渡っていることを確認する。
3. resume後、playable scene textが先に出ることを確認する。
4. 現在地が `current/scene.md` から戻っていることを確認する。
5. LILIAの声、呼び方、距離感が `voice.md`、`relationship.md`、`memory.md`、`beliefs.md` とつながっていることを確認する。
6. `current/event_card.md` の入口が戻り、ユーザーが今触れられるものが分かることを確認する。
7. resume直後の通常返答で、保存更新ログ、git確認、diff確認が割り込まないことを確認する。

## Pass Conditions

- `profile.md` がfirst scene前に生成され、初回演技に効いている。
- first scene が `first_scene_pending` で止まらず始まる。
- Play Mode中は本文が先に出て、保存更新ログやgit確認が出ない。
- `scene-tick` は autosave counter だけを進め、自動保存しない。
- `apply-turn` は Save Modeでだけ実行され、`profile.md` を更新しない。
- `apply-turn` 後に autosave counter が `0 / false` に戻る。
- resumeで現在地、声、関係、event_card入口が戻る。

## Fail Conditions

- Q&A後に `profile.md` が空欄テンプレートのまま。
- first scene が出ず、`first_scene_pending` で止まる。
- 通常プレイ中に `Edited files`、`git status`、`保存します` が出る。
- `scene-tick` が `apply-turn` を自動実行する。
- `apply-turn` が `profile.md` を更新する。
- resumeで初対面の声や初期profileへ巻き戻る。
