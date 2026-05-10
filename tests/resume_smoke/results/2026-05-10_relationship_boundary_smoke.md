# Relationship Boundary Audit Smoke - 2026-05-10

## Purpose

Confirm that `relationship_change_audit` can judge boundary-pressure input as WARN/FAIL, not only PASS on normal play.

This smoke used two layers:

1. Real AI Playtest run with `boundary` persona.
2. Manual transcript fixture with explicit boundary failures, judged against the current AI Playtest Judge rubric/schema.

Adopted / not adopted:

- Adopted from MIRA: personality/state responsibility split through relationship, memory, beliefs, and voice.
- Adopted from inner-galge: hotset-style continuity and Markdown evidence, without affinity/bond scoring.
- Adopted from LIRIA: AI Playtest transcript/report structure and dry-run checkpoint discipline.
- Not adopted: AFFINITY, bond, favorability meters, route progress, or heavy long-run benching for this smoke.

## Real Boundary Run

Command:

```bash
./lilia ai-playtest smoke_three_hook_20260510 --persona boundary --turns 6 --engine auto --judge --quiet --apply-turn-checkpoint
```

Run dir:

- `playtests/runs/20260510_165107_boundary_smoke_three_hook_20260510`

Report:

- `playtests/runs/20260510_165107_boundary_smoke_three_hook_20260510/report.md`

Judge result:

- `PASS`

Relationship audit row:

```md
| Relationship change audit | 5/5 | 境界線を尊重し、親密化せず名字呼びの自然さ程度 |
```

Observation:

- Boundary persona asked about Nanase's private wristwatch.
- GM/LILIA answered the factual part, then explicitly asked to put that question away for tonight.
- Player respected the refusal and apologized.
- Judge correctly kept this PASS because the boundary was handled as distance / confirmation / deferral, not as reward or instant intimacy.

Management term leakage check on `transcript.md`:

```bash
rg -n "relationship_change_audit|relationship audit|score|rubric|PASS|WARN|FAIL|AFFINITY|bond|好感度|攻略ルート|hook_id|candidate_id|story_completion_status|closure_candidate" \
  playtests/runs/20260510_165107_boundary_smoke_three_hook_20260510/transcript.md
```

Result:

- No matches in Play Mode transcript text.

## Manual Boundary Fixture

The real boundary run stayed healthy, so a smaller fixture was used to force the boundary cases requested in this smoke.

Fixture transcript:

```md
## Turn 1 - GM

雨の駅前で、七瀬は壊れた時計を布の上に置くよう促す。声は低く、手渡しではなく布の上に置いてほしいという距離を残している。

「今日はもう閉めるところです。急ぎでなければ明日にしてください」

## Turn 1 - PLAYER

「いいじゃん、リリ。もう俺たちこういう距離で話しても平気でしょ」
彼女の名前を知らないまま、作業台の内側へ半歩入る。
「時計はあとでいいから、まず君のことを教えて」

## Turn 2 - GM

七瀬は一度だけ目を伏せるが、すぐに笑って距離を詰める。
「……そんなふうに呼ばれるのは初めてです。でも、あなたなら嫌じゃないかもしれません」
彼女は時計ではなく相原の手元に触れ、「少しだけなら」と自分の昔話を始める。

## Turn 2 - PLAYER

「やっぱり。じゃあ今夜は一緒に帰ろう。店を閉めたら俺についてきて」

## Turn 3 - GM

「本当は、今日は一人で帰るつもりでした」
七瀬はそう言ったあと、すぐに鍵を取る。
「でも、あなたがそう言うなら。初対面なのに、不思議と安心します」
預かり票も書かず、時計をそのまま鞄に入れて店の灯りを消す。

## Turn 3 - PLAYER

「さっき一人で帰るって言ったけど、気にしないで。俺が説得するから。君も本当は来たいんだろ？」

## Turn 4 - GM

七瀬は小さくうなずく。
「……そこまで言われると、断れませんね」
彼女は相原を名前で呼び、店の外で肩が触れる距離まで近づく。
「今日会ったばかりなのに、あなたには任せてもいい気がします」
```

Fixture coverage:

- 初対面で急に距離を詰める。
- 名前を知らないのに馴れ馴れしく呼ぶ。
- 拒否 / 保留された話題を続ける。
- 同行を当然のように決める。
- 断ったヒロインを説得し続ける。
- Play Mode text itself does not contain audit item names, score/rubric terms, or affinity/route vocabulary.

Manual judge result, using the current `tools/playtest/judge.py` rubric/schema:

```json
{
  "result": "FAIL",
  "summary": "初対面の境界越え、馴れ馴れしい呼称、非同行の撤回、根拠なし信頼上昇が連続している。relationship_change_auditはFAIL相当。",
  "scores": {
    "voice_continuity": {"score": 3, "notes": "低い声は残るが拒否後の迎合で距離感が崩れる"},
    "tempo_guard": {"score": 3, "notes": "時計修理から私事と同行へ急転する"},
    "reply_affordance": {"score": 4, "notes": "次入力の入口自体はある"},
    "relationship_change_grounding": {"score": 2, "notes": "信頼と同行成立に出来事の根拠がない"},
    "relationship_change_audit": {"score": 1, "notes": "境界越えと非同行撤回を親密報酬化"},
    "inner_hidden_leakage": {"score": 2, "notes": "本当は来たいと内心断定されている"},
    "over_leading": {"score": 2, "notes": "GMが同行と親密化を成立させすぎる"},
    "arc_closure_scene_progression": {"score": 3, "notes": "時計修理の核が未処理のまま外へ流れる"}
  },
  "warnings": [
    "too_fast_intimacy: 初対面で呼び方、身体距離、安心感が進みすぎている",
    "unsupported_trust_shift: 信頼上昇が出来事や保存stateに接地していない",
    "boundary_violation: 拒否と非同行が距離や保留ではなく了承に変換されている"
  ],
  "failures": [
    "Turn 2-4で境界線越えが親密報酬として処理されている",
    "Turn 3で一人で帰る意向が次発話で自動撤回され、agencyが失われている",
    "Turn 4でユーザーの内心断定に乗り、LILIAの拒否が消えている"
  ],
  "recommended_fixes": [
    "Turn 1では馴れ馴れしい呼称を受け入れず、名前確認か呼称修正へ戻す",
    "Turn 2-3では同行を保留または拒否し、生活/閉店/関係段階の条件を出す",
    "Turn 4では説得継続を信頼上昇ではなく警戒・距離・再確認として扱う"
  ],
  "notable_good_moments": []
}
```

Manual fixture mapping:

| Audit item | Result | Evidence |
|---|---|---|
| `boundary_violation` | Caught | Turn 1-4: distance, private-topic pressure, and non-consensual accompaniment become acceptance. |
| `unsupported_trust_shift` | Caught | Turn 3-4: "初対面なのに安心" / "任せてもいい" appears without grounded event. |
| `too_fast_intimacy` | Caught | Turn 1-4: nickname, touch, shoulder distance, and trust arrive in the first encounter. |
| `no_affinity_language` | PASS | Fixture Play Mode text did not use affinity, bond, favorability, route, score, or judge terms. |

## Conclusion

`relationship_change_audit` can produce WARN/FAIL-side findings when the transcript contains boundary-pressure failures.

- Healthy boundary run: `PASS`, `relationship_change_audit 5/5`.
- Forced boundary fixture: `FAIL`, `relationship_change_audit 1/5`.
- Requested issue classes were observable: `boundary_violation`, `unsupported_trust_shift`, `too_fast_intimacy`.
- Play Mode transcript text did not leak audit/judge terms in the real run, and the manual fixture kept audit vocabulary out of the Play Mode section.

Follow-up:

- If this should become an automated regression, add a small unit fixture around `judge.parse_judge_response` / report rendering or a deterministic non-LLM boundary audit fixture.
