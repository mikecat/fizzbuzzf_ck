FizzBuzzF\*ck
============

## これは何？

FizzBuzzを0バイトで実装することを可能にした、Brainf\*\*k派生言語。

## 言語仕様 (概要)

* 基本的には[Brainf\*\*k](https://www.muppetlabs.com/~breadbox/bf/)と同じである。
* プログラムの実行開始直前に、配列にFizzBuzzの出力となる文字列を格納する。
* プログラムの実行完了後、ポインタの現在位置から右にポインタを進めながら、ゼロの直前の要素までを出力する。

## 関連記事

* [FizzBuzzを0byteで実装する - Qiita](https://qiita.com/mikecat_mixc/items/100a06731b053659d040)

## What is this?

A language derived from Brainf\*\*k which enables to implement FizzBuzz in 0 bytes.

## Language Specification (abstract)

* Basically the same as [Brainf\*\*k](https://www.muppetlabs.com/~breadbox/bf/).
* Store the output of FizzBuzz just before starting execution of the program.
* After the execution of the program finished, print each elements of the array from the current position of the pointer before first element whose value is zero, moving the pointer to the right.
