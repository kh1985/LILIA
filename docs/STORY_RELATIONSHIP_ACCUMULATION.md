# LILIA Story / Relationship Accumulation Loop

この文書は、イベントがLILIAとの関係の物語として積み重なる仕組みを定義する設計正本です。
実装コード、CLI、full plot生成ではなく、Markdown stateとevent_card運用のための軽量ルールです。

## 1. LILIAの中核

LILIAは、単なるAIチャットでも固定恋愛ゲームでもない。

LILIAは、会話、選択、物語を記憶し、関係性と人格の出方が少しずつ変化するAI恋愛シミュレーションである。

ストーリーやイベントは主役ではない。
ストーリーやイベントは、LILIAの人格、記憶、信頼、距離感、声、境界線、beliefsを変化させるための装置である。

イベントが起きただけではストーリーではない。
その出来事にLILIAが自然に反応し、ユーザーの選択が関係に残り、次の第一声や距離感が変わった時に、LILIAのストーリーが進む。

## 2. Source Of Truth

- 中核思想: `docs/CORE_CONCEPT.md`
- state構造: `docs/STATE_STRUCTURE.md`
- event_card可プレイ性: `docs/EVENT_CARD_PLAYABILITY.md`
- growth update: `docs/GROWTH_UPDATE_LOOP.md`
- voice continuity: `docs/VOICE_CONTINUITY.md`
- romance / intimacy growth: `docs/ROMANCE_INTIMACY_GROWTH.md`
- style reference: `prompt/style_reference.md`
- save / resume: `prompt/save_resume.md`

この文書は、event、story、story reference、NPC tier、World Autonomy / Pressureの位置づけの正本である。
event_cardの必須項目は `docs/EVENT_CARD_PLAYABILITY.md`、保存更新先は `docs/GROWTH_UPDATE_LOOP.md` を優先する。

## 3. Event / Story の違い

`Event` は点である。
今この瞬間に起きる出来事、ユーザーが触れる入口、LILIAが反応する状況を指す。

`Story` は線である。
イベントが積み重なって、LILIAとの関係に意味が生まれた流れを指す。

LILIAでは、敵を倒したことや事件を解決したことだけがストーリー進行ではない。
記憶、信頼、距離感、声、呼び方、境界線、beliefsが変わることがストーリー進行である。

例:

- Event: LILIAが消えた通知ログに気づく。
- Story: その違和感をユーザーがどう扱ったかで、LILIAが自分の記憶を信じられるか、ユーザーへ不安を見せられるかが変わる。

この例は説明であり、固定イベントではない。

## 4. キャラ人格とイベント進行を両立する原則

イベントでLILIAを動かさない。
LILIAの人格が自然に反応する状況を置く。

その反応とユーザーの選択が、`memory.md`、`relationship.md`、`beliefs.md`、`voice.md` に残ることでストーリーになる。

見る順序:

1. LILIAの人格、価値観、怖さ、守りたいものを見る。
2. それに刺さる出来事を置く。
3. LILIAが自然に反応する。
4. ユーザーが触れる。
5. 何が残ったかを保存する。
6. 次の第一声、距離、event_cardが変わる。

scene終了や章区切りでSave Modeに入る時は、必要に応じて `next_hook` を残す。
next_hookはfull plotではなく、未回収札、約束、通知、相談、持ち物、仕事相談や便利屋依頼などから、次にユーザーが自然に返せる入口を1つ作るための短い橋である。
`apply-turn` では `current/event_card.md` に `Next Hook`、`story/story_deck.md` に `Candidate Next Hook` として保存する。

イベントの都合でLILIAを急に別人格にしない。
LILIAの反応が何も変わらないなら、その出来事はLILIAのストーリーでは弱い。

## 5. Story Reference Engine

Story Reference Engine は、参照作品や過去知見から、本文、固有名詞、台詞、キャラ、展開順を使う仕組みではない。

採用するのは、旧LIRIAの Story Reference Layer と、inner-galge の `エピソードタイプ -> 参考作品 -> 感情の骨 -> 現在キャラへ変換 -> 分岐点 -> 書く` という抽象化手順である。

手順:

1. 今のsceneで動かしたい関係変化を一行で置く。
2. selection signals を2-4個選ぶ。
3. 候補engineを3-5個まで短く出す。
4. 採用engineを1-3個までに絞る。
5. 参照元から、感情の骨、抽象構造、選択の力学だけを抜く。
6. LILIAの `core / voice / state / relationship / memory / beliefs` に合わせて具体化する。
7. `current/event_card.md`、`story/story_deck.md`、`story/relationship_spine.md` に分けて保存する。
   文体や表現軸が必要な場合だけ `style/reference.md` に短く分離する。

禁止:

- 参照作品の固有名詞を使う。
- 参照元の台詞を使う。
- 参照元のキャラ配置を使う。
- 参照元の展開順をなぞる。
- 本文に作品名や参照元を出す。

参照は模倣ではなく、感情の骨を現在のLILIAとの関係へ変換するために使う。
Story Reference Engine は物語と関係の抽象構造を扱う。
`style/reference.md` は文体、視点距離、描写密度、余韻の置き場であり、story referenceの正本にはしない。

参考カタログ:

`references/story_media_stock.md` に50作品のカタログがある。
Selection Signals が決まり、Reference Engine を選んだ後、必要なら Quick Selection Guide から候補作品を3-5個に絞る。
採用は1-3個までにする。
作品名や固有要素は本文に出さない。
感情の骨と抽象構造だけを抜く。

## 6. LILIA版 Selection Signals

Selection Signals は、いまのevent/storyがどの関係温度を動かすかを見るための軽量タグである。
固定ジャンルや選択肢ではない。

- `romance / sweetness`: 甘さ、照れ、身体距離、言い残し、翌朝の第一声。
- `daily / life`: 食事、眠気、帰る場所、通知、部屋、生活の足場。
- `memory / promise`: 約束、覚えていたこと、忘れていたこと、保留した言葉。
- `boundary / intimacy`: 触れる/触れない、合意、止まれる余地、aftercare。
- `secret / unsent`: 送らなかった言葉、言えない理由、隠した不安。
- `self-recognition`: LILIAが自分をどう見直すか、弱さや欲しさを認めるか。
- `institution / record`: 記録、ログ、本人性、保存された言葉、消えた履歴。
- `organization / ideology`: 誰かの思想、圧、巻き込みたくない相手、黙る理由。
- `ability / rule`: 反応条件、制約、言える/言えない境界、記憶の欠落。

初期MVPでは、`romance / sweetness`、`daily / life`、`memory / promise`、`boundary / intimacy` を優先する。
`organization / ideology` や `ability / rule` は重くしすぎず、LILIAの関係に刺さる小さな圧として扱う。

## 7. LILIA版 Reference Engine

Reference Engine は、eventを作るための抽象エンジンである。
engine名は内部の設計ラベルであり、作中本文に出さない。

### Unsaid Feeling Engine

言えない気持ち、言いかけて止める、沈黙、返信の遅れを扱う。
LILIAの声、距離、第一反応に出す。

### Memory Promise Engine

約束、覚えていたこと、忘れていたこと、守れなかったことを扱う。
`memory.md` と `relationship.md` に残る節目を作る。

### Boundary / Consent Engine

触れる、触れない、待つ、止まる、確認する、aftercareを扱う。
親密sceneを報酬化せず、関係段階と境界線を動かす。

### Inherited Wound Engine

LILIAの怖さ、過去の痛み、守っているもの、繰り返したくない反応を扱う。
`core.md` を上書きせず、`beliefs.md` と `relationship.md` に揺れを残す。

### Institution / Record Engine

記録のズレ、保存された言葉、消えたログ、本人性、LILIAの記憶の不安を扱う。
重い組織やcase_engineではなく、LILIAが自分の記憶をどう信じるかに接続する。

### Charismatic Contact Engine

短い接触でLILIAやユーザーの判断を揺らす人物、言葉、誘いを扱う。
NPCをすぐKey NPC化せず、tierに応じて薄く始める。

### Secret Organization Engine

LILIAが言えない理由、巻き込みたくない相手、信頼するか黙るかを扱う。
初期MVPでは重い組織、敵幹部、勢力図を作らない。

### Rule-Bound Constraint Engine

能力、規則、制約、言える/言えない境界、記憶の欠落を扱う。
戦闘や能力バトルではなく、LILIAの反応条件と関係リスクへ落とす。

## 8. 抽象化から具体化への変換

参照元の構造は、そのままLILIAへ持ち込まない。
感情の骨を、現在の関係、場所、声、event_cardへ変換する。

- romance source -> 視線、沈黙、約束、身体距離、aftercare、翌朝の第一声。
- institution source -> 記録のズレ、保存された言葉、消えたログ、本人性、LILIAの記憶の不安。
- organization source -> LILIAが言えない理由、巻き込みたくない相手、信頼するか黙るか。
- ability / rule source -> LILIAの反応条件、言える/言えない境界、記憶の欠落、制約。
- place source -> 部屋、画面、通知、夜、食事、眠気、帰る場所。

変換時は、以下を分ける。

- known: 実際に起きたこと、見えていること、保存された事実。
- suspected: LILIA側の仮説、誤解、疑い、まだ確認していないつながり。
- unknown: 隠してよい真相、未確定の理由、まだ出さない札。

knownは `memory.md` や `event_card.md` へ、suspectedは `beliefs.md` や `story_deck.md` へ、unknownは必要なら `story_deck.md` の未回収札へ置く。
ユーザーの内面は、本人の入力なしにknownへしない。

## 9. 基本ループ

Story / Relationship Accumulation の基本ループは以下である。

1. LILIAの人格を見る。
2. 出来事がLILIAの何かに刺さる。
3. LILIAが自然に反応する。
4. ユーザーが選ぶ。
5. `memory / relationship / beliefs / voice` が変わる。
6. 次の第一声やevent_cardが変わる。
7. これが積み重なってストーリーになる。

このループでは、full plotを先に作らない。
イベントごとの反応と保存更新が線になり、後からストーリーとして読める状態を作る。

## 10. イベントを作る時の5問

event_cardやstory_deckへ新しい出来事を置く前に、以下を短く見る。

- これはLILIAの何に刺さる？
- LILIAは人格的にどう反応する？
- ユーザーは何に触れる？
- 何が残る？
- 次回どう戻ってくる？

答えられない場合は、出来事を大きくするのではなく、LILIAの関係に刺さる入口へ小さく直す。

## 11. NPC Tiering

NPCは最初から全員を作り込まない。
LILIAの記憶、関係、beliefsに影響した時だけ段階的に昇格させる。

### Tier 0: Atmosphere / 背景

場所の気配、名前のない人影、通知の向こうの存在。
保存しない。

### Tier 1: Mob Contact / 一時接触NPC

一度だけ触れる相手。
event_card入口や短い圧として使う。

### Tier 2: Scene NPC / 場面NPC

そのsceneのvisible problemに関わる相手。
名前や役割があり、LILIAのstateを少し動かす。

### Tier 3: Recurring NPC / 再登場NPC

再登場し、memory / beliefs / relationship に影響する相手。
story_deckの未回収札と接続する。

### Tier 4: Key NPC / キーNPC

LILIAのcore、fear、boundary、secretに刺さる相手。
複数eventにまたがり、LILIAの声や距離感を変える。

### Tier 5: LILIA-level Character

MVPでは原則禁止。
LILIAと同格の関係存在を増やす場合は、MVP後の別設計にする。

## 12. NPC昇格条件

昇格は、設定を増やすためではなく、LILIAとの関係に影響した時だけ行う。

- Tier 0 -> 1: ユーザーが触れた、event_card入口になった、LILIAの反応に関係した。
- Tier 1 -> 2: 名前や役割が出た、LILIAのstateが変わった、visible problemに関わった。
- Tier 2 -> 3: 再登場した、memory / beliefs / relationshipに影響した、story_deck未回収札に関わった。
- Tier 3 -> 4: LILIAのcore / fear / boundary / secretに刺さる、複数eventにまたがる、LILIAの声や距離感を変える。
- Tier 4 -> 5: 原則しない。MVP後の別設計。

NPCを昇格させる時は、何がLILIAに残ったかを先に見る。
NPCの設定量ではなく、LILIAの反応と記憶への影響で判断する。

## 13. NPCの保存先

- Tier 0: 保存しない。
- Tier 1: `current/event_card.md` または `story/story_deck.md` の短いメモ。
- Tier 2: `story/story_deck.md` / `current/event_card.md`。
- Tier 3: `story/npc/<id>.md` を検討。
- Tier 4: `story/npc/<id>.md` 必須。
- Tier 5: MVPでは原則作らない。

`cast/npc` は初期MVPでは標準にしない。
必要になったら後続で検討する。

`story/npc/<id>.md` を導入する場合も、保存するのはNPCの全プロフィールではない。
LILIAとの関係に効く観測、役割、再登場条件、known / suspected / unknown、LILIAの反応への影響に絞る。

## 14. 生成粒度

生成粒度は、保存先ごとに分ける。

- `current/event_card.md`: 具体的に作る。今ユーザーが触れる入口、visible problem、first concrete actionを持つ。
- NPC: tierに応じて作る。Tier 0-1は薄く、Tier 3以上だけ個別ファイルを検討する。
- `story/story_deck.md`: 素材、圧、未回収札として作る。現在sceneそのものにはしない。
- `story/relationship_spine.md`: 方向性として作る。固定プロットにしない。
- story_reference: 抽象構造として作る。参照作品の本文や固有名詞を保存しない。
- full plot: 作らない。

初期MVPでは、今触れるevent_cardを優先し、長いプロット表やNPC辞典を作らない。

## 15. World Autonomy / Pressure の扱い

World Autonomy / Pressure Loop は消さない。
ただし上位概念ではなく、Story / Relationship Accumulation Loop の下位要素として扱う。

大きな世界が勝手に動くのではない。
放置した出来事、未回収札、言い残し、境界線、約束、記録のズレが、1-3 scene後に小さく戻ることとして扱う。

使ってよい圧:

- 返信が遅れる。
- 消えたログがもう一度目に入る。
- 約束の時間が近づく。
- LILIAが避けていた話題に触れざるを得なくなる。
- NPCが短く再接触する。
- 未回収札がevent_cardの入口へ前景化する。

避ける圧:

- 親密sceneを雑な事件乱入で壊す。
- 巨大組織や敵幹部を急に出す。
- LILIAの人格や境界線を無視して強制進行する。
- case_engine / villain_engine / combatを初期MVPに持ち込む。

外圧は、LILIAとの関係を壊すためではなく、記憶、信頼、距離、言い残しを次のsceneへ返すために使う。

## 16. 中心文

LILIAのイベントは、人格を動かす命令ではなく、人格が自然に反応する状況である。

ストーリーは、その反応とユーザーの選択が記憶、関係、beliefsに残り、次のLILIAの声と距離感を変えることで進む。

参照作品や漫画は、その構造を模倣するためではなく、感情の骨を抽出し、LILIAとの関係に刺さる形へ具体化するために使う。

NPCは最初から全員を作り込まず、LILIAの記憶、関係、beliefsに影響した時だけ段階的に昇格させる。

## 17. Gate Failure Conditions

- eventがLILIAの人格や関係に刺さらない。
- storyが固定プロットになり、LILIAの反応やユーザーの選択を無視して進む。
- 参照作品の固有名詞、台詞、キャラ、展開順を模倣している。
- NPCを最初から全員ヒロイン級に作り込んでいる。
- World Autonomy / Pressureが親密sceneを壊す乱入になっている。
- story_deckが現在sceneの可視eventそのものになっている。
- event_cardがstory_deckの抽象札だけで、ユーザーが触れる入口を持たない。
- known / suspected / unknown が混ざり、推測や未確定情報がmemoryの事実になっている。
- 官能表現が安全の名目で消されている。

## 18. Gate Passing Conditions

- eventが、LILIAの人格、記憶、関係、beliefs、voiceのどこに刺さるか分かる。
- storyが、eventの積み重なりとして、次の第一声、距離、event_cardへ戻ってくる。
- 参照作品は感情の骨、抽象構造、選択の力学だけとして扱われている。
- event_card、story_deck、relationship_spine、style/referenceの責務が混ざっていない。
- NPCがtierに応じた粒度で扱われ、LILIAを食わない。
- known / suspected / unknown が分かれ、memoryには実際に起きたことだけが入る。
- World Autonomy / Pressureが、放置した出来事や未回収札の小さな戻りとして機能している。
- 親密sceneを雑な乱入で壊さず、aftercare、境界線、言い残しへ接続している。

## 19. Adopted From

- MIRA: 状態分離、known / suspected / unknown、事実、推測、場面表現の分離。
- inner-galge: 参考作品から感情の骨を抽出し、現在キャラと状況へ変換する手順。
- LIRIA: Story Reference Layer、selection signals、candidate shortlist、Reference Engine、event_card / story_deck / relationship_spine の運用。

## 20. Not Adopted

- 参照作品の固有名詞、台詞、キャラ、展開順の模倣。
- 旧ハーレム攻略、kaneco固有、旧AFFINITY。
- NPC全員をヒロイン級に作り込む運用。
- full plotを事前生成する運用。
- 重い組織、敵幹部、case_engine、villain_engine、combatを初期MVPに入れること。
- 親密sceneを雑な事件乱入で壊す運用。
- 官能表現そのものの削除。

## 21. Reason

event_cardやGrowth Update Loopが整っても、イベントがストーリーへ積み重なる仕組みとNPCの分類、昇格条件が未定義だと、プレイ中に支離滅裂になりやすい。

LILIAは人格と関係が中心なので、ストーリーは固定プロットではなく、出来事が記憶、関係、beliefsへ残る線として扱う必要がある。

参照作品は模倣ではなく、感情の骨を抽出してLILIAの関係へ具体化するために使う必要がある。

NPCは薄すぎるとイベントが霧になり、濃すぎるとLILIAを食う。
そのため、tier分類と昇格条件を置き、LILIAの記憶、関係、beliefsに影響した時だけ段階的に作り込む。
