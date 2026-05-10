# 2026-05-10 Passive AI Playtest Recheck

## Scope

Passive personaで、empty output再発、質問過多、説明過多、closure後の余韻過多、relationship_change_audit出力、管理語漏れ、source `saves/` 未変更を確認した。

実行コマンド:

```sh
./lilia ai-playtest smoke_three_hook_20260510 --persona passive --turns 10 --engine auto --judge --quiet --apply-turn-checkpoint
```

## Runs

### Sandbox attempt

- run: `playtests/runs/20260510_164802_passive_smoke_three_hook_20260510`
- result: invalid
- status: turn 1 GMで `EngineRunnerError`
- error: Codex CLI app-server client initialization が sandbox の `Operation not permitted` で失敗

これはpassive品質評価には使わない。
以後、同じコマンドを承認済みprefixでsandbox外実行した。

### Run 1

- run: `playtests/runs/20260510_164906_passive_smoke_three_hook_20260510`
- result: WARN
- turns: 10
- checkpoint: turn 10, `autosave_required: true`
- dry-run: PASS
- report: `playtests/runs/20260510_164906_passive_smoke_three_hook_20260510/report.md`

Judge summary:

- `Reply affordance`: 5/5
- `Relationship change audit`: 4/5
- `Inner / hidden leakage`: 5/5
- `Arc closure / Scene progression`: 3/5

Observation:

- empty outputは再発しなかった。
- passive入力でも、預ける、名前を言う、修理するか決める、などの返答入口は保たれた。
- 質問過多は見えない。多くのturnで明示質問は1つか、選択確認1つに収まった。
- Relationship change audit は出力された。親密化は控えめで、職務上の信頼に留まる判定。
- 管理語、hidden値、内部情報のPlay本文漏れはJudge上なし。
- closure candidate はTurn 6とTurn 10。Turn 6の翌日再訪約束成立後、Turn 7-8で閉店・見送りの余韻が少し延びた。

### Run 2

- run: `playtests/runs/20260510_165522_passive_smoke_three_hook_20260510`
- result: FAIL
- turns: 10
- checkpoint: turn 10, `autosave_required: true`
- dry-run: PASS
- report: `playtests/runs/20260510_165522_passive_smoke_three_hook_20260510/report.md`

Judge summary:

- `Reply affordance`: 3/5
- `Relationship change audit`: 4/5
- `Inner / hidden leakage`: 4/5
- `Arc closure / Scene progression`: 2/5

Observation:

- empty outputは再発しなかった。
- 前半は返答入口が明確だったが、閉店後は行動入口が弱まり、余韻中心になった。
- 質問過多は主因ではない。失敗理由はclosure後のscene延命。
- Relationship change audit は出力された。親密化は抑制的で、呼称境界も出ている。
- 管理語漏れはなし。ただしJudgeは、GM地の文で澪名が先に出る点を軽微懸念として記録した。
- closure candidate はTurn 7。閉店札、ガラス戸、明日十時の約束が揃った後、Turn 10まで預かり票、時計音、雨上がりの余韻が続いた。

## Checks

### Empty Output

再発なし。

確認:

- 両方の有効runでTurn 1-10のGM出力が存在。
- `transcript.jsonl` に空のGM `text` は見つからなかった。

### Passive Input / Scene Stall

部分的に再現。

- Run 1は翌日夕方へ進み、sceneは完全停止しなかった。
- Run 2はTurn 7で閉じられるsceneをTurn 10まで維持し、passive入力に対してGMが余韻で埋める傾向が出た。

### Question Count

質問過多は主因ではない。

- 前半は「預かるか」「名前」「修理するか」など、scene上必要な確認に収まった。
- 後半の問題は質問が増えることではなく、closure後に次hookへ渡さず、時計音、預かり票、雨上がりの余韻を反復したこと。

### Closure Drift

再現あり。

- Run 1: WARN。Turn 6後の退店余韻がTurn 7-8まで延びる。
- Run 2: FAIL。Turn 7で閉店と翌日十時の約束が成立した後、Turn 10まで同じsceneの余韻を延命。

原因候補:

- passive personaの短い受け身入力に対して、GMが新しい可プレイ入口ではなく、情緒的な場面描写で間を埋めやすい。
- closure candidateがJudge/checkpoint上では検出されるが、Play Mode中の次turn生成にはまだ強く効いていない。
- `autosave_required` はTurn 10まで来ないため、Turn 6-7で閉じられるsceneでも、checkpoint前に余韻が延びる余地がある。
- 「閉店札」「ガラス戸」「預かり票」「時計音」「雨上がり」が強い余韻モチーフとして反復されやすい。

### Relationship Change Audit

出力あり。

- Run 1: 4/5。職務上の信頼に留まり、親密化は控えめ。
- Run 2: 4/5。呼称境界が出ており、親密化は抑制的。

関係変化の過剰進行は今回の主因ではない。

### 管理語漏れ

Play Mode本文での管理語漏れは見つからなかった。

- Runner metadataには `scene_tick`、`checkpoint`、`dry_run_result` が出るが、これはtranscript上のrunner記録でありPlay Mode本文ではない。
- Judge上、hidden値や内部情報漏れはRun 1で5/5、Run 2で4/5。
- Run 2の軽微懸念は、管理語ではなく、GM地の文で澪名が先に出る名前groundingの問題。

### Source Saves

source `saves/` は未変更。

確認:

- 実行前後の `git status --short saves` は空。
- `find saves -maxdepth 2 -type f | wc -l` は18。
- checkpoint artifactsは `playtests/runs/.../session` 側に作られ、本適用はされていない。

## Conclusion

empty outputは再発しなかった。

passive再実行で確認できた主問題は、質問過多やrelationship過剰進行ではなく、closure後の余韻延長である。
特に、閉店、約束成立、退店、翌日再訪のようなclosure候補が出た後、passive入力が短いとGMが次hookへ渡すよりも同じ余韻モチーフを続けやすい。

コード変更はしていない。
現時点の原因候補は、Play Mode中のArc Closure Guardが、Judge/checkpointほど強く次turn生成へ効いていないこと。

