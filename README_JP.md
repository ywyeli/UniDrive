<p align="right">English | <a href="./README_CN.md">简体中文</a> | <a href="./README_JP.md">日本語</a></p>  


<p align="center">
  <img src="assets/figs/unidrive-logo.png" align="center" width="20%">
  
  <h3 align="center"><strong>UniDrive: カメラ構成全体にわたるユニバーサルドライビング認識に向けて</strong></h3>

  <p align="center">
      <a href="https://ywyeli.github.io/" target='_blank'>Ye Li</a><sup>1</sup>&nbsp;&nbsp;&nbsp;
      <a href="https://wzzheng.net/" target='_blank'>Wenzhao Zheng</a><sup>2</sup>&nbsp;&nbsp;&nbsp;
      <a href="https://robotics.umich.edu/profile/xiaonan-sean-huang/" target='_blank'>Xiaonan Huang</a><sup>1</sup>&nbsp;&nbsp;&nbsp;
      <a href="https://people.eecs.berkeley.edu/~keutzer/" target='_blank'>Kurt Keutzer</a><sup>2</sup>
  <br />
  <sup>1</sup>ミシガン大学アナーバー校&nbsp;&nbsp;&nbsp;
  <sup>2</sup>カリフォルニア大学バークレー校&nbsp;&nbsp;&nbsp;
  </p>

</p>

<p align="center">
  <a href="https://arxiv.org/abs/2410.13864" target='_blank'>
    <img src="https://img.shields.io/badge/Paper-%F0%9F%93%83-slategray">
  </a>
  
  <a href="https://wzzheng.net/UniDrive" target='_blank'>
    <img src="https://img.shields.io/badge/Project-%F0%9F%94%97-lightblue">
  </a>
  
  <a href="" target='_blank'>
    <img src="https://img.shields.io/badge/Demo-%F0%9F%8E%AC-pink">
  </a>
  
  <a href="" target='_blank'>
    <img src="https://img.shields.io/badge/%E4%B8%AD%E8%AF%91%E7%89%88-%F0%9F%90%BC-red">
  </a>
  
  <a href="" target='_blank'>
    <img src="https://visitor-badge.laobi.icu/badge?page_id=ywyeli.UniDrive&left_color=gray&right_color=firebrick">
  </a>
</p>


## 概要

`UniDrive`は、マルチカメラ構成全体で認識モデルを一般化する課題に対処するために設計された新しいフレームワークです。
- 私たちの知る限り、UniDriveは多様なカメラ構成全体でビジョン中心の3D認識モデルを一般化するために設計された最初の包括的なフレームワークです。
- 画像を統一された仮想カメラスペースに変換する新しい戦略を導入し、カメラパラメータの変動に対するロバスト性を向上させます。
- 投影誤差を最小限に抑える仮想構成最適化戦略を提案し、最小限の性能低下でモデルの一般化を向上させます。
- システマティックなデータ生成プラットフォームと160,000フレームのマルチカメラデータセットを提供し、異なるカメラ構成全体で認識モデルを評価するベンチマークを提供します。

[プロジェクトページ](https://wzzheng.net/UniDrive)を訪れて、さらに多くの例を探索してください。:blue_car:


## :hammer_and_wrench: UniDrive パイプライン
| <img src="assets/figs/pipeline.png" align="center" width="98%"> |
| :-: | 
| 入力画像を統一された仮想カメラスペースに変換して、ユニバーサルドライビング認識を実現します。仮想ビューでのピクセルの深度を推定するために、地面認識深度仮定戦略を提案します。複数の実カメラ構成に対して最も効果的な仮想カメラスペースを取得するために、投影誤差を最小限に抑えるデータ駆動型最適化戦略を提案します。 |


## 更新情報

- \[2024.10\] - 私たちの[論文](https://arxiv.org/abs/2410.13864)がarXivで公開されました。



## アウトライン

- [インストール](#gear-installation)
- [データ準備](#hotsprings-data-preparation)
- [カメラ構成](#blue_car-camera-configuration)
- [始めに](#rocket-getting-started)
- [UniDrive ベンチマーク](#bar_chart-UniDrive-benchmark)
- [TODO リスト](#memo-todo-list)
- [引用](#citation)
- [ライセンス](#license)
- [謝辞](#acknowledgements)



## :gear: インストール

インストールと環境設定に関する詳細については、[INSTALL.md](assets/INSTALL.md)を参照してください。



## :hotsprings: データ準備

`UniDrive`データセットは、既存の自動運転構成からインスピレーションを得た合計8つのカメラ構成で構成されています。

各カメラ構成には4〜8個のセンサーが含まれています。各カメラ構成について、サブデータセットは20,000フレームのサンプルで構成されており、10,000サンプルがトレーニング用、10,000サンプルが検証用です。

| <img src="assets/figs/town01.png" align="center" width="125"> | <img src="assets/figs/town03.png" align="center" width="125"> | <img src="assets/figs/town04.png" align="center" width="125"> | <img src="assets/figs/town06.png" align="center" width="125">
| :-: | :-: | :-: | :-: | 
| タウン1 | タウン3 | タウン4 | タウン6 |

CARLA v0.9.10の4つのマップ（タウン1、3、4、6）を選択して、点群データを収集し、グラウンドトゥルース情報を生成します。各マップについて、すべての道路をカバーするために6つのエゴビークルルートを手動で設定し、重複する道路はありません。シミュレーションの頻度は20 Hzに設定されています。

私たちのデータセットは[OpenDataLab](https://opendatalab.com/)によってホストされています。
><img src="https://raw.githubusercontent.com/opendatalab/dsdl-sdk/2ae5264a7ce1ae6116720478f8fa9e59556bed41/resources/opendatalab.svg" width="32%"/><br>
> OpenDataLabは、大規模AIモデル時代のための先駆的なオープンデータプラットフォームであり、データセットをアクセス可能にします。OpenDataLabを使用することで、研究者はさまざまな分野の無料のフォーマット済みデータセットを取得できます。

`UniDrive`データセットの準備の詳細については、[DATA_PREPARE.md](assets/document/DATA_PREPARE.md)を参照してください。



## :blue_car: カメラ構成

| <img src="assets/figs/4x.png" align="center" width="210"> | <img src="assets/figs/5x.png" align="center" width="210"> | <img src="assets/figs/6x60.png" align="center" width="210"> | <img src="assets/figs/6x70.png" align="center" width="210"> |
| :-: | :-: | :-: | :-: |
| 4x95 | 5x75 | 6x60 | 6x70 |
| <img src="assets/figs/6x80a.png" align="center" width="210"> | <img src="assets/figs/6x80b.png" align="center" width="210"> | <img src="assets/figs/nuScenes.jpg" align="center" width="210"> | <img src="assets/figs/8x.png" align="center" width="210">
| 6x80a | 6x80b | 5x70+110 | 8x50 | 



## :rocket: 始めに

このコードベースの使用方法について詳しくは、[GET_STARTED.md](assets/GET_STARTED.md)を参照してください。




## :bar_chart: UniDrive ベンチマーク


## :memo: TODO リスト
- [ ] 初期リリース。🚀
- [ ] カメラ構成ベンチマークを追加。
- [ ] さらに多くの3D認識モデルを追加。



## 引用
この研究があなたの研究に役立つ場合は、私たちの論文を引用してください：

```bibtex
 @article{li2024unidrive,
            title={UniDrive: Towards Universal Driving Perception Across Camera Configurations},
            author={Li, Ye and Zheng, Wenzhao and Huang, Xiaonan and Keutzer, Kurt},
            journal={arXiv preprint arXiv:2410.13864},
            year={2024}
          }
```


## ライセンス

この作品は<a rel="license" href="">MITライセンス</a>の下にありますが、このコードベースの特定の実装には他のライセンスが含まれている場合があります。商業的な目的でコードを使用する場合は、[LICENSE.md](assets/LICENSE.md)を参照して、より注意深く確認してください。



## 謝辞

この作品は[MMDetection3D](https://github.com/open-mmlab/mmdetection3d)コードベースに基づいて開発されています。

> <img src="https://github.com/open-mmlab/mmdetection3d/blob/main/resources/mmdet3d-logo.png" width="31%"/><br>
> MMDetection3Dは、PyTorchに基づくオープンソースのツールボックスであり、一般的な3D認識のための次世代プラットフォームを目指しています。これは、MMLabによって開発されたOpenMMLabプロジェクトの一部です。

