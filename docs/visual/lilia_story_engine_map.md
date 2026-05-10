# LILIA 物語エンジン Mermaid マップ

このファイルは、LILIAの物語エンジン構造をMermaidで素早く確認するための可視化メモです。
目的は、仕様を増やすことではなく、「分かりやすさ」と「面白さを生む作用」を図で把握することです。

特定セッションや特定題材には依存しません。

## 1. 全体循環

LILIAの全体循環です。入力は本文出力で終わらず、状態更新と次の入口候補を通って、次の入力へ戻ります。

```mermaid
flowchart TD
  UI["ユーザー入力<br/>発言・行動・沈黙"]
  THS["3本の入口軸<br/>入力を内部で受け止める"]
  PO["プレイヤーの足場<br/>何の話か分かる状態"]
  AEC["現在のイベントカード<br/>今触れる入口"]
  SCL["物語の因果層<br/>何に作用し何を変えるか"]
  PMO["プレイ本文<br/>表示される本文"]
  SUC["保存候補<br/>次回へ残す変化"]
  SAVE["保存確定<br/>Save Mode / apply-turn"]
  MRBV["記憶 / 関係 / 認識 / 声<br/>次回以降に効く状態"]
  SDCH["物語デッキ / 候補入口<br/>未回収札・次候補"]
  NAH["次の前景入口<br/>次に触れる入口"]

  UI --> THS --> PO --> AEC --> SCL --> PMO --> SUC --> SAVE --> MRBV --> SDCH --> NAH --> UI
```

注記: プレイ本文の中では保存処理を見せない。保存候補は、Save Mode / apply-turn を通って初めて確定保存される。

## 2. 1ターン処理

1ターンの内部処理です。状態ファイルは本文へそのまま出すのではなく、今必要な一手へ変換します。

```mermaid
flowchart TD
  UI["ユーザー入力"]
  PARSE["行動・発言と内心を分ける"]
  SCENE["現在場面ファイルを読む<br/>現在地・直前の出来事"]
  EVENT["イベントカードを読む<br/>今触れる入口"]
  INTERNAL["声 / 一時状態 / 関係 / 記憶 / 認識を読む<br/>必要な材料だけ使う"]
  FOCUS["この1ターンの焦点を1つに絞る"]
  REACT["ヒロインの反応を作る"]
  MOVE["1つだけ動かす<br/>状況・関係・情報のどれか"]
  ENTRANCE["次に返せる入口を残す"]
  NOTE["状態ファイルを全部本文に出すのではなく、今必要な一手へ変換する。"]

  UI --> PARSE --> SCENE --> EVENT --> INTERNAL --> FOCUS --> REACT --> MOVE --> ENTRANCE
  FOCUS -.-> NOTE
```

## 3. 要素関係図

物語要素の関係図です。場面開始時に持つもの、ユーザー入力で動くもの、場面終了時に残るものを分けます。

```mermaid
graph TD
  subgraph START["場面開始時に持つもの"]
    PO["プレイヤーの足場<br/>これは何の話かを理解する"]
    DQ["この場面で追う問い"]
    VP["見えている問題<br/>場面上で何が普通ではないか"]
    WFM["欲求 / 恐れ / 誤信<br/>キャラの内側の圧"]
    AEC["現在のイベントカード<br/>今触れる入口と変化の束"]
  end

  subgraph INPUT["ユーザー入力で動くもの"]
    DC["会話の衝突<br/>目的や受け取り方のズレ"]
    CT["選択の緊張<br/>なぜ迷うのか"]
    CAU["因果<br/>行動が何に作用し何を変えるか"]
  end

  subgraph ENDING["場面終了時に残るもの"]
    DELTA["不可逆の変化<br/>場面後に元へ戻らない差分"]
    MRBV["記憶 / 関係 / 認識 / 声<br/>次回以降に効く保存状態"]
    NC["次の好奇心<br/>次に知りたくなる問い"]
    SDCH["物語デッキ / 候補入口<br/>未回収札・次場面候補"]
  end

  PO --> DQ
  DQ --> VP
  VP --> CT
  AEC --> PO
  AEC --> VP
  WFM --> DC
  DC --> CT
  CT --> CAU
  CAU --> DELTA
  DELTA --> MRBV
  DELTA --> NC
  NC --> SDCH
  SDCH --> AEC
```

## 4. 3本の入口軸

3本の入口軸は選択肢UIではありません。自由入力を内部で受け止め、プレイモードではそのうち1本だけが前景入口としてイベントカードに出ます。

```mermaid
flowchart TD
  UI["ユーザー入力<br/>自由な発言・行動・沈黙"]
  ABSORB["3本の入口軸が入力を受け止める<br/>選択肢ではなく内部の戻り道"]
  MAIN["外側の出来事<br/>依頼・事件・小さな謎・仕事・街の圧"]
  REL["関係の入口<br/>距離・信頼・誤解・約束・境界線"]
  LIFE["生活探索の入口<br/>生活・移動・遠出・仕事・帰宅・日常"]
  ACTIVE["前景入口を1本だけ選ぶ"]
  CARD["現在のイベントカード<br/>今この場で触れる形にする"]

  UI --> ABSORB
  ABSORB --> MAIN
  ABSORB --> REL
  ABSORB --> LIFE
  MAIN --> ACTIVE
  REL --> ACTIVE
  LIFE --> ACTIVE
  ACTIVE --> CARD
```

## 5. 物語の三層

筋立て・感情・意味の三層です。場面は、何が起きるかだけでなく、何が揺れて何に意味が生まれるかで面白くなります。

```mermaid
graph TB
  subgraph PLOT["筋立ての層"]
    P1["現在場面"]
    P2["イベントカード"]
    P3["物語デッキ"]
    P4["前景入口"]
    PQ["問い:<br/>何が起きるか<br/>次に何をするか<br/>何が普通ではないか"]
  end

  subgraph EMOTION["感情の層"]
    E1["一時状態"]
    E2["関係"]
    E3["記憶"]
    E4["認識・思い込み"]
    E5["声・距離感"]
    EQ["問い:<br/>誰が何を望むか<br/>何を恐れるか<br/>どう受け取るか<br/>関係がどう揺れるか"]
  end

  subgraph MEANING["意味の層"]
    M1["関係の背骨"]
    M2["人格の核"]
    M3["テーマ"]
    M4["矛盾"]
    MQ["問い:<br/>この関係は何を問うのか<br/>何が変わると物語として意味があるのか<br/>どんな価値観がぶつかるのか"]
  end

  PLOT --> EMOTION --> MEANING
  FORMULA["面白い場面 = 筋立てが動く + 感情が揺れる + 意味が少し変わる"]
  PLOT --> FORMULA
  EMOTION --> FORMULA
  MEANING --> FORMULA
```

## 6. 場面機能の診断タグ

物語を進める15機能です。これは固定プロット順ではなく、場面の役割を診断するためのタグ群です。

各機能の意味:

- 主役: 誰を追う話か
- 前提: どんな暮らし・ルールの上にあるか
- 起点: 何が日常を揺らすか
- 目標: 何を求めて動くか
- 始動: なぜ一歩踏み出すか
- 試練: 何が難しいか
- 糸口: 次へ進む足場
- 前進: 何が少し進んだか
- 転回: 問題の意味がどう変わったか
- 孤立: 何を失い、自分で選ぶか
- 奈落: 関係や心が最も沈む点
- 打開: 積み上げたものが突破口になる
- 選択: 中心問題にどう答えるか
- 着地: 何が決まり、何が変わったか
- 余韻: どんな感情と次の問いが残るか

```mermaid
flowchart TB
  subgraph EARLY["導入・始動を見るタグ"]
    F01["主役"]
    F02["前提"]
    F03["起点"]
    F04["目標"]
    F05["始動"]
  end

  subgraph PROGRESS["進行を見るタグ"]
    F06["試練"]
    F07["糸口"]
    F08["前進"]
    F09["転回"]
  end

  subgraph PRESSURE["圧力を見るタグ"]
    F10["孤立"]
    F11["奈落"]
  end

  subgraph RESOLVE["解決・余韻を見るタグ"]
    F12["打開"]
    F13["選択"]
    F14["着地"]
    F15["余韻"]
  end

  EARLY --> PROGRESS --> PRESSURE --> RESOLVE
```

注記: これは固定プロット順ではなく、場面の役割を診断するための道具。毎回この順番で処理するものではない。

## 7. 状態遷移図

イベントカード / 入口候補の状態遷移です。前景化された入口は、進展、停滞、悪化、解決、保存へ分岐します。

```mermaid
stateDiagram-v2
  candidate: 候補
  active: 前景化
  advanced: 進展
  blocked: 停滞
  worsened: 悪化
  resolved: 解決
  archived: 保存済み

  [*] --> candidate
  candidate --> active: 前景化する
  active --> advanced: ユーザーが触れる
  active --> blocked: 境界線 / 条件不足
  active --> worsened: 放置 / 扱いを誤る
  advanced --> resolved: 終了条件を満たす
  resolved --> archived: 保存される
  advanced --> candidate: 次の好奇心が入口を作る
  archived --> [*]
```

## 8. 1ターンのやり取り

1ターン内のやり取りです。プレイモードは状態を読み、前景化された入口を見て本文を作りますが、保存処理そのものは本文に出しません。

```mermaid
sequenceDiagram
  participant Player as プレイヤー
  participant PlayMode as プレイモード
  participant StateFiles as 状態ファイル
  participant EventCard as イベントカード
  participant Heroine as ヒロイン
  participant SaveCandidates as 保存候補

  Player->>PlayMode: 行動 / 発言
  PlayMode->>StateFiles: 現在の状態を読む
  PlayMode->>EventCard: 前景化された入口を読む
  PlayMode->>PlayMode: この1ターンの焦点を選ぶ
  PlayMode->>Heroine: 反応を生成する
  Heroine-->>Player: プレイ可能な場面本文
  PlayMode->>SaveCandidates: 残りうる変化を覚えておく
  Note over PlayMode,SaveCandidates: プレイモードでは保存処理を本文に出さない。
```
