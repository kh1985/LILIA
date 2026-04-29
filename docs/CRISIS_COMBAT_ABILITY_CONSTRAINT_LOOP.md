# Crisis / Combat / Ability Constraint Loop

この文書は、LILIAにおける危機、戦闘、能力使用を、関係変化へ接続するための設計正本である。
実装コード、CLI、combat engine、数値バトルではなく、Markdown stateとevent_card運用のための軽量ルールを定義する。

## 1. Purpose

Crisis / Combat / Ability Constraint Loop は、LILIAにおける危機、戦闘、能力使用を、勝敗処理ではなく、関係、記憶、beliefs、voice、自己理解に残る揺れとして扱うためのループである。

危機や戦闘は、敵を倒したかどうか、HPが残ったかどうか、どちらが強いかだけで判断しない。
LILIAが何を怖がったか、何を守ろうとしたか、ユーザーをどう見直したか、次の第一声や距離感がどう変わるかを見る。

能力は便利な解決ボタンではない。
能力には、できること、できないこと、条件、代償、痕跡、関係リスク、状態変化が必要である。

この文書は、重い戦闘ルールブックではない。
危機を `current/event_card.md` の visible problem として扱い、結果を必要分だけ `state`、`memory`、`relationship`、`beliefs`、`voice`、`story_deck` へ残すための正本である。

## 2. Source Of Truth

- 中核思想: `docs/CORE_CONCEPT.md`
- state構造: `docs/STATE_STRUCTURE.md`
- event_card可プレイ性: `docs/EVENT_CARD_PLAYABILITY.md`
- 保存更新: `docs/GROWTH_UPDATE_LOOP.md`
- story / relationship accumulation: `docs/STORY_RELATIONSHIP_ACCUMULATION.md`
- romance / intimacy growth: `docs/ROMANCE_INTIMACY_GROWTH.md`
- prompt core: `prompt/core.md`
- new開始: `prompt/newgame.md`
- save / resume: `prompt/save_resume.md`

この文書は、Crisis / Combat / Ability Constraint の位置づけの正本である。
event_cardの必須項目は `docs/EVENT_CARD_PLAYABILITY.md`、保存更新先は `docs/GROWTH_UPDATE_LOOP.md`、eventがstoryへ積み重なる扱いは `docs/STORY_RELATIONSHIP_ACCUMULATION.md` を優先する。

## 3. LILIAにおける危機・戦闘・能力の位置づけ

危機は、LILIAの人格、信頼、境界線、恐れ、守りたいもの、ユーザーへの見方を揺らす状況である。

戦闘は、敵を倒すための数値ゲームではない。
LILIAでは、逃げる、守る、隠す、交渉する、耐える、助けを呼ぶ、能力を使う、代償を払うことを含む危機対応として扱う。

能力は、万能解決ではない。
能力は、危機に触れるための一手であり、関係リスクと痕跡を伴う。
能力を使ったことで何が残り、何を隠せなくなり、LILIAが何を見直すかまで見る。

危機の結果は、次の第一声、沈黙、呼び方、警戒、信頼、距離感に戻る。
危機が終わっても、LILIAの声や関係に何も残らないなら、その危機はLILIAの体験として弱い。

## 4. Crisis / Combat / Ability の違い

- `Crisis`: 今、何かが危うくなっている状況。必ずしも戦闘ではない。
- `Combat`: 身体的、社会的、心理的、能力的な衝突を含む危機対応。数値バトルに限定しない。
- `Ability`: プレイヤーまたはLILIAが使える特殊な手段。ただし制約、代償、痕跡、関係リスクを持つ。

`Crisis` は `current/event_card.md` の visible problem になる。
ユーザーが今触れる入口を持ち、何が危ういか、最初に何へ触れるかが分かる必要がある。

`Combat` は `Crisis` への対応の一部である。
戦うことだけでなく、逃げる、待つ、隠す、止める、話す、頼る、手放すことも含む。

`Ability` は `Combat` や `Crisis` を解くための一手である。
ただし、万能ボタンではない。
能力は、使った時にも、使わなかった時にも、関係と記憶に残る余地を持つ。

## 5. 勝敗ではなく関係と自己理解を揺らす原則

危機は、「勝った / 負けた」だけで終わらせない。
危機後には、以下を見る。

- 何を守ったか。
- 何を失ったか。
- 何を隠したか。
- 誰に頼ったか。
- 誰を頼らなかったか。
- LILIAがユーザーをどう見直したか。
- LILIAが自分自身をどう見直したか。
- ユーザーがLILIAの境界線をどう扱ったか。
- 能力使用の代償が次に何を変えるか。

悪い扱い:

- 敵を倒したので終了。
- 能力で全部解決した。
- LILIAがイベント都合で急に戦う。
- 親密sceneに危機を乱入させて中断する。
- 勝ったのに、LILIAの第一声、距離、警戒、記憶が何も変わらない。

良い扱い:

- 逃げたことで、LILIAが「守られた」より「置いていかれなかった」と感じる。
- 能力を使った痕跡が残り、次のsceneでLILIAがユーザーの無理に気づく。
- 守る選択をしたが、LILIAの自尊心や境界線に小さな摩擦が残る。
- 助けを呼んだことで、信頼は増えるが秘密が少し広がる。

これらは説明用の例であり、固定イベントではない。
実際のsceneでは、LILIAの人格、現在の関係、直前の記憶、ユーザーの入力に合わせて変換する。

## 6. 行動選択の同等性

以下は同じ重さの危機対応として扱う。

- 逃げる。
- 守る。
- 交渉する。
- 隠す。
- 耐える。
- 助けを呼ぶ。
- 能力を使う。
- 代償を払う。
- 何かを諦める。
- あえて戦わない。

戦うことだけを正解にしない。
能力を使うことだけを正解にしない。

逃げる、止まる、助けを呼ぶ、隠す、謝る、待つ、手放すことも、関係に残る有効な選択である。
その選択がLILIAにどう見えたか、信頼、警戒、境界線、沈黙、次の第一声に何を残すかを見る。

行動の価値は、勝敗ではなく、何を守り、何を残し、何を変えたかで判断する。

## 7. Ability Constraint

能力は、以下の項目で軽量管理する。

- `core`: 能力の本質。
- `can`: できること。
- `cannot`: できないこと。
- `condition`: 使える条件。
- `cost`: 払う代償。
- `trace`: 残る痕跡。
- `risk`: 関係や状況へのリスク。
- `state impact`: 疲労、動揺、負傷、沈黙などの状態変化。
- `relationship impact`: 信頼、警戒、依存、距離感への影響。
- `belief impact`: LILIAが何を信じ直すか、疑うか。

能力の制約は、能力を弱くするためではない。
能力を使った結果が、LILIAとの関係、記憶、beliefs、voiceへ残るようにするためである。

禁止:

- 新しい能力をその場の都合で生やす。
- できないことを消す。
- 代償なしで便利に使う。
- 能力でLILIAの感情や境界線を雑に突破する。
- 能力でユーザーの内面やLILIAの内面を勝手にknown化する。
- 能力を使えば必ず正解になる構造にする。
- 能力を使わない選択を失敗扱いに固定する。

`cannot` は重要である。
できないことがあるから、逃げる、交渉する、助けを呼ぶ、待つ、諦めるなどの選択に意味が出る。

## 8. event_cardへの接続

危機は `current/event_card.md` の visible problem として扱う。

危機event_cardに必要な観点:

- `visible problem`: 何が危ういか。
- `first concrete action`: 最初に何へ触れるか。
- `handles`: 戦う以外の行動余地。
- `relationship stake`: LILIAとの関係に何が残りうるか。
- `if ignored`: 放置したら何が小さく変わるか。
- `next visible change`: 次に見える変化。
- `Story Residue`: `memory`、`relationship`、`beliefs`、`voice` に何が残るか。

危機event_cardは、抽象的な「危ない気配」だけでは足りない。
ユーザーが今触れる入口を持つ必要がある。

真相は隠してよい。
ただし、何が危ういか、最初に何へ触れられるか、LILIAとの関係に何が残りうるかは隠さない。

危機を大きくしすぎない。
初期MVPでは、巨大な敵組織や戦闘システムではなく、LILIAの記憶、信頼、境界線、声に刺さる可視入口として置く。

## 9. state / memory / relationship / beliefs / voice への保存

危機後は、全部を保存しない。
何が変わったかを見て、必要なファイルだけ短く更新する。

- `state`: 疲労、動揺、負傷、眠気、集中切れ、回復途中など。
- `memory`: 実際に起きたこと、守ったこと、逃げたこと、能力使用、約束、拒否、保留。
- `relationship`: 信頼、警戒、距離感、境界線、頼り方、頼られ方。
- `beliefs`: LILIA側の仮説、疑い、見直し、まだ確認していない解釈。
- `voice`: 危機後の第一声、呼び方、沈黙、冗談の減り方、声の硬さ、甘さ、避け方。
- `story_deck`: 未回収の痕跡、戻ってくる圧、能力使用の余波、NPC接触の残り。

memoryには実際に起きたことだけを書く。
suspected / unknown をmemoryの事実にしない。

beliefsには、LILIA側の仮説として残す。
ユーザーの内面や本心を、本人の入力なしに確定しない。

stateには今だけの状態を置く。
能力使用後の疲労、動揺、警戒、集中切れはstateに置けるが、それだけで長期関係の結論にしない。

voiceは、継続的に変わる時だけ更新する。
一時的な声の硬さや沈黙は、必要ならstateやhotsetに短く置く。

## 10. story_deck / relationship_spine への戻し方

危機の余波は `story/story_deck.md` へ未回収札として戻せる。

戻してよいもの:

- ability trace。
- 関係リスク。
- まだ説明していない痕跡。
- 1-3 scene後に小さく戻る圧。
- NPCや接触相手の短い再接触条件。
- LILIAがまだ言えていない不安。
- ユーザーが気づいていないが、LILIAの反応に残っている変化。

ability traceや関係リスクは、1-3 scene後に小さく戻る圧として扱える。
大きな世界が勝手に動くのではなく、言い残し、記録のズレ、体調の戻らなさ、避けた話題、声の硬さとして返す。

`story/relationship_spine.md` には、固定プロットではなく、危機後に変わりうる方向性だけを置く。

例:

- 信頼が増えたが、LILIAが無理を見抜くようになる。
- 守られたが、LILIAが自分の弱さを嫌がる。
- 能力の痕跡を見て、LILIAがユーザーを心配するが、踏み込みすぎない。

これらは説明用の例であり、固定イベントではない。
relationship_spineを攻略ルートや章立てプロットにしない。

## 11. 親密sceneを雑に壊さない境界

親密scene中に、雑な襲撃や危機乱入で中断しない。

危機を入れる場合は、親密sceneそのものを破壊するのではなく、以下として扱う。

- aftercare。
- 言い残し。
- 境界線。
- 翌朝の第一声。
- 沈黙。
- 生活圧。
- 後で戻る未回収札。

Crisis / Combat / Ability Constraint Loop は、Romance / Intimacy Growth Loop と衝突してはいけない。
親密さは危機への報酬ではなく、危機は親密さへの罰ではない。

危機で親密さを罰しない。
親密さを危機への報酬にも罰にも使わない。

親密scene前後では、成人、合意、相互性、境界線、止まれる余地、aftercareを優先する。
外圧や能力の痕跡は、関係に接続する小さな戻りとして扱い、乱入のための装置にしない。

## 12. MVP範囲

初期MVPに入れるもの:

- 危機をevent_cardとして扱う。
- 戦う以外の対応を同じ重さで扱う。
- ability constraintを軽量に持つ。
- `cost`、`trace`、`relationship risk` を扱う。
- 結果を `state`、`memory`、`relationship`、`beliefs`、`voice` へ必要分だけ残す。
- `story_deck` へ余波や未回収札を戻す。
- 危機後の第一声、沈黙、信頼、警戒、距離感を見る。
- 能力を使わない選択にも意味を残す。

初期MVPでは、今触れるevent_cardと保存更新を優先する。
戦闘の細かい処理や敵の作り込みではなく、LILIAとの関係に何が残るかを優先する。

## 13. 採用しないもの

初期MVPで採用しないもの:

- HP管理。
- ダメージ計算。
- 部位管理。
- 行動順。
- 戦闘マップ。
- 敵幹部。
- 巨大組織戦。
- 勢力図。
- combat engine。
- villain_engine。
- case_engine。
- 能力ツリー。
- スキル成長表。
- 戦闘ログ解析。
- full plot。
- キャンペーン進行表。
- 親密sceneへの雑な乱入。

これらは、必要になった場合でも後続設計で扱う。
初期MVPでは、敵、組織、能力体系を主役にしない。
主役はLILIAとの関係変化である。

## 14. Gate Failure Conditions

以下のどれかに当てはまる場合、このLoopは失敗している。

- 危機がLILIAとの関係に何も残らない。
- 戦うことだけが正解になっている。
- 能力が代償なしの万能解決になっている。
- できないことが消えている。
- 痕跡や関係リスクがない。
- LILIAの境界線や人格を能力で突破している。
- 危機がevent_cardのvisible problemになっていない。
- ユーザーが今何に触れられるか分からない。
- 親密sceneを雑な襲撃で壊している。
- memoryに推測や未確定情報を書いている。
- beliefsでユーザーの内面を断定している。
- 敵やNPCが主役化している。
- 勝敗処理だけで、第一声、距離感、沈黙、信頼、警戒に戻ってこない。
- story_deckが重い組織設定やfull plot置き場になっている。

## 15. Gate Passing Conditions

以下を満たす場合、このLoopは通過している。

- 危機がvisible problemとしてユーザーに触れる入口を持つ。
- 戦う以外の行動余地がある。
- 能力に `can`、`cannot`、`cost`、`trace`、`risk` がある。
- 能力を使わない選択にも意味がある。
- 危機の結果が `state`、`memory`、`relationship`、`beliefs`、`voice` の必要箇所に残る。
- memoryには実際に起きたことだけが入る。
- beliefsにはLILIA側の仮説として疑い、見直し、更新条件が残る。
- LILIAの第一声、距離感、沈黙、信頼、警戒に戻る余地がある。
- 親密sceneを雑に壊していない。
- NPCや敵がLILIAとの関係を照らす補助に留まっている。
- story_deckへ戻す余波が短く整理されている。
- event_card、story_deck、relationship_spineの責務が混ざっていない。

## 16. 中心文

LILIAにおける危機・戦闘・能力は、勝敗や攻略のための処理ではなく、LILIAとの関係、記憶、beliefs、voice、自己理解を揺らすための状況である。

戦う、逃げる、守る、交渉する、隠す、耐える、助けを呼ぶ、能力を使うことは同じ重さの選択であり、能力は代償、痕跡、関係リスクを持つ。

危機の結果は、次の第一声、距離感、沈黙、信頼、警戒として戻ってくる。

## 17. Reason

event_cardやStory / Relationship Accumulationが整っても、危機や能力が万能解決になると、LILIAとの関係が薄くなる。

combatを重くしすぎると、LILIAの主役が関係から戦闘システムへ移ってしまう。
敵、組織、能力体系が前に出すぎると、LILIAの人格、記憶、声、距離感が背景化する。

ability constraintを持たないと、能力が便利ボタンになり、記憶、信頼、境界線、代償が残らない。
できることだけでなく、できないこと、使う条件、残る痕跡、関係リスクを見ることで、能力は関係を揺らす選択になる。

初期MVPでは、危機を軽く扱いながら、関係に残る余波を作ることが重要である。
危機は、LILIAをイベント都合で動かす命令ではなく、LILIAの人格が自然に反応する状況として置く。
