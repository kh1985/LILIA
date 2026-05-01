# LILIA Persona Profile

この文書は、`lilia/main/profile.md` の目的と責務を定義する設計正本です。

## 1. Purpose

`profile.md` は、初回scene前からLILIAを演じられるようにするための人格正本である。

LILIAは、初回から生活、行動、矛盾、反応、禁忌を持つ。
ただし、`profile.md` は完成済み攻略キャラカードではない。
恋愛感情、親密成立、攻略トリガー、固定台詞集を事前に完成させない。

目的は、初回sceneで人格の空白を詩的比喩や雰囲気だけで埋めないことにある。
生活上の役割、具体物、困った時の反応、褒められた時の反応、踏み込まれた時の境界線を、first scene前に持たせる。

## 2. Adopted From inner-galge

inner-galge の character system から採用するもの:

- 自然言語指示から character YAML を作る流れ。
- `name / age / occupation / appearance / tone / personality / reactions / forbidden / context` の素材化。
- personalityを形容詞ではなく行動で書く方針。
- 登場前に、声、生活、反応、矛盾、禁忌を1枚にまとめる考え方。
- Markdownで人間が読める形にする運用。

## 3. Changed For LILIA

LILIAでは、inner-galge の `cast/heroine/*.md` を復活させない。

`profile.md` は、1人のLILIAが記憶と関係の中で育つための初期正本である。
複数ヒロイン、ハーレム、攻略ルート、AFFINITY、bond、エロ到達度を正本化しない。

character YAMLは素材であり、LILIAの最終正本ではない。
YAMLから `lilia/main/profile.md` を生成し、first scene前に読む。
`scripts/lilia_generate_character_yaml.py` はstandalone wrapperとしてClaude CLIを実際に呼べる。
ただし `./lilia` launcherは外部character YAML生成を自動実行しない。
自動生成を使わない場合は、GM/AIが同じschemaでYAML相当を作る。

## 4. File Responsibility

`profile.md` に置くもの:

- 基礎情報。
- toneの基準。
- 行動で見えるpersonality。
- values、everyday anchors、memories、contradictions、unspoken。
- reactions、forbidden、context。
- fixed memoryの初期分類。
- 5層構造 / Self-Understanding。
- voice by relationship stage。
- Relationship Progressionの軽量分類。
- Multi-Relationship / Jealousy Profile の latent slot。
- Ability / Intimacy Resonance の dormant slot。
- Deepening Tags。
- Do Not Predefine。

`profile.md` に置かないもの:

- 完成された恋愛感情。
- ユーザーへの好意。
- 攻略トリガー。
- 親密成立。
- 重い過去の全説明。
- 固定台詞集。
- ハーレム展開の強制。
- 能力反応の即時発火。

## 5. Separation From Main State

`profile.md` は初回演技の人格正本である。
ただし、関係で育った内容は以下へ分解して保存する。

- `core.md`: profileから抽出された最小の変わらない核、価値観、譲れないもの。
- `voice.md`: 継続的に変わった呼び方、声、沈黙、距離の出方。
- `state.md`: 今だけの感情、疲労、照れ、警戒、保留。
- `relationship.md`: 距離、信頼、境界線、相互性、intimacy / consent / boundary。
- `memory.md`: 実際に起きた出来事、約束、拒否、保留、aftercare。
- `beliefs.md`: LILIA側の仮説、誤解、疑い、見直し。

責務の境界:

- `profile.md`: 初期の生活、職能、行動、矛盾、反応、禁忌。
- `core.md`: 短期都合で変えてはいけない核だけ。profileの要約やコピーではない。
- `voice.md`: 声、呼び方、関係段階別の変化。
- `memory.md`: 実際に起きたこと。
- `relationship.md`: ユーザーとの距離、信頼、境界線の現在形。
- `beliefs.md`: LILIA側の仮説。

`profile.md` を毎ターン肥大化させない。
毎回の会話ログや関係変化は、`profile.md` ではなく該当する正本へ保存する。
profileを全部の正本にしない。

## 6. First Scene Use

first scene前には必ず `profile.md` を読む。

初回sceneでは、`profile.md` にある以下を使う。

- 生活上の場所。
- 仕事 / 用事 / 習慣。
- よく触る物。
- 初回sceneで使える具体物。
- 表の態度と内側の矛盾。
- 急かされた時、踏み込まれた時、待ってもらえた時の反応。
- forbidden。

初回sceneでは、LILIAを完成させない。
ユーザーの選択に対する反応を観察し、その後に `core / voice / relationship / memory / beliefs` へ必要分だけ保存する。

## 7. Resume Use

通常resumeで毎回 `profile.md` 全文を読む必要はない。

読む場面:

- `first_scene_pending` の時。
- voice崩れや人格崩れがある時。
- `voice / relationship / memory / beliefs` が不足している時。
- 関係段階の確認が必要な時。
- 初回sceneの生活上の具体物や矛盾を再確認したい時。

hotsetだけでprofileを代替しない。
一方で、profile全文を毎ターン総読みしてテンポを壊さない。

`profile.md` は初期人格正本だが、現在の関係・記憶より優先しない。
実際に起きた変化は `memory.md`、`relationship.md`、`beliefs.md`、`voice.md` を優先する。
矛盾した場合は、profileを初期状態として扱い、育ったLILIAを初期profileへ巻き戻さない。

## 8. Latent / Dormant Slots

Multi-Relationship / Jealousy Profile は `latent` として持つ。

嫉妬は、好感度ペナルティではない。
他者との関係をLILIAへの否定として自動処理しない。
初期から嫉妬イベントを強制しない。

Ability / Intimacy Resonance は `dormant` として持つ。

能力は初期sceneでは使わない。
能力が導入された場合だけ、LILIAの体質や感覚、境界線、合意、memory / relationship / beliefs への保存先を確認する。
合意なしに能力で親密さを進めない。

## 9. Deepening Tags

Deepening Tags は攻略チェックリストではない。

Deepening Tags は、関係に残った節目の索引である。
タグが埋まったから親密さが解放されるわけではない。
実際に起きた会話、拒否、約束、摩擦、aftercare、境界確認だけを、必要な正本へ保存する。

## 10. Character YAML Handling

character YAMLのbase schema:

- `name`
- `age`
- `occupation`
- `appearance.hair_style`
- `appearance.hair_color`
- `appearance.notes`
- `tone.rule`
- `tone.examples`
- `personality`
- `reactions`
- `forbidden`
- `context.backstory`
- `context.current_situation`

変換時の注意:

- `personality` は形容詞ではなく行動として移す。
- `context` は `context`、`memories`、`everyday anchors` へ分ける。
- `reactions` はLILIA用の反応欄へ拡張する。
- `forbidden` は境界線と禁忌へ入れる。
- values / contradictions / unspoken / Layer構造 / relationship progression は、Q&AとYAMLから必要最小限だけ補う。
- 深い過去や恋愛成立を勝手に作らない。

## 11. Not Adopted

- `cast/heroine` の復活。
- 複数ヒロイン前提。
- ハーレム名称。
- AFFINITY数値。
- bond数値。
- エロ到達度。
- 好感度ペナルティ。
- 攻略ルート。
- 固定台詞集。
- 初回から能力や親密反応を発火させる運用。

## 12. Reason

現状のLILIAは、Q&A結果を `core / voice / state / relationship / memory / beliefs` に分散できる。
一方で、first scene前に「このLILIAをどう演じるか」が1枚にまとまっていないと、初回sceneで人格の空白を雰囲気だけで埋めやすい。

`profile.md` は、その空白を埋める。
ただし、関係で育つ余白を消さない。
