---
layout: post
author: keiran  
title: "Quantum Chem's NextGen Lang Trifecta: Hartree–Fock in Rust, Julia, and Python."
category: code
tags: Hartree-Fock Python Julia Rust code tutorial 
---

[Program in C](https://youtu.be/tas0O586t80?si=H2HnFcVoS4tNqKB0) they said. It's good for you they said. [And it is!](https://youtu.be/hE7l6Adoiiw?si=Ourgha7DTfRy_Cer)
That is until you step outside the bounds of an array. Or dereference the wrong pointer to an array of pointers. Or, heaven forbid in this chatty age, want to do text processing.
C is *fast*, it allocates memory like machine code. But it's not the only game in town, and [not always the fastest](https://www.i-programmer.info/news/98-languages/15506-rust-fast-and-safe.html). 
C++ gives you a lot of powerful language features. But I don't write in it, I never took enterprise software engineering and I like to keep my digital shotguns well away from my feet.

> "C makes it easy to shoot yourself in the foot; C++ makes it harder, but when you do it blows your whole leg off".

--- [Bjarne Stroustrup](https://www.stroustrup.com/quotes.html), developer of the C++ programming language

So let's reimplement the fundamental orbital energy optimiser, the basis for all [electronic structure theory methods]({% post_url 2023-04-12-compchem-methods-basics %}): Hartree--Fock.  <span style="color:#A9A9A9">(With deep debt to [QUACCS](https://quaccs.wordpress.com/))</span>

In with the new (apologies Formula Translation maintainence work); so for pedagogical/andragogical reasons, and to learn a couple of new languages, let's write the same algo in three languages:

- 🦀 `Rust`: It's all the rage, faster than C, and very nicely gives you a talking to when it can see mistakes in the future.
- 🐍 `Python`: It's Python! It's everywhere. It's *readable*. It's not so bad as you would think because core Numerical Python is implemented in highly optimised C anyway. 
- 🔴🟢🟣 `Julia`: "[*as flexible as Python, as numerical as Matlab, as fast as Fortran, and as deep as Lisp.*](https://discourse.julialang.org/t/elevator-pitch/29457/8)". Designed *for* scientific computing. Well, what's not to like? It's REPL prompt is super nice, it's package manager doesn't make me prematurely age like Python does in my day job. And Just-In-Time compilation is *incredibly smart*. <span style="color:#A9A9A9">(I secretly think this is why observables are indeterminate until measured, but today we're strictly ["Shut up and calculate"](https://hsm.stackexchange.com/questions/3615/who-was-the-first-to-say-shut-up-and-calculate))</span> 

With [WebAssembly](https://rust-lang.org/what/wasm/) and [Pluto notebooks](https://plutojl.org/) we can do quantum chemistry in our browser. Let's goooo--- 

---

The Hartree--Fock algorithm is the computational kernel for more accurate [electronic structure wavefunction methods]({% post_url 2023-04-12-compchem-methods-basics %}), where electron behaviour is improved by addition of either 'dynamic' electron correlation (mutual repulsion during motion) and 'static' correlation (fun stuff where a single arrangement of reference electron orbitals are insufficient). First we need to get a reasonable set of combined atomic orbitals for the resting state of a molecule. I'm using "pre-baked" basis-sets as really I want to focus on the algorithm (Roothaan--Hall eigenvalue finding) and coding it up.

So, we're starting with a set of atomic orbitals ($$\chi_{n}$$) (here, the minimal viable ones, the basis-set). We combine them to get some set of molecular orbitals ($$\phi_{i} = \sum\limits_{n}C_{ni}\chi_{n}$$) (MOs). If we take these electrons and capture their properties as spin--$$\frac{1}{2}$$ particles---kinetic energy, attraction to nuclei, electron--electron repulsions, change of sign upon indistinguishable particle exchange (Fermi stats)--- we get the Fock operator $$\hat{F}$$ to work with. Really, the Fock operator is related to the overlap of orbital basis set vectors ($${S}$$), and we can use an algorithm to optimise the co-efficients ($${C}$$) of these orbitals to lower the orbital energies ($$\epsilon$$)

So we have the Roothan--Hall matrix optimisation problem of finding the co-efficients that lowers the molecular orbital energies, which is guaranteed to be the closest to ground-state reality for HF (the Variational Principle).

$$\mathbf{FC} =  \epsilon \mathbf{SC}$$ 

Right, enough notation. Let's set up an engine that finds the energy eigenvalues ($$\epsilon$$) given some input orbitals, and then uses and optimisation algorithm to feed the output co-efficients back in to iteratively refind until converge. Yielding a set of one-electron orbitals solved in "self-consistent field" with respect to the other electrons. Time to code. 

 
> Code snippets will be as quotes. Blocks will be syntax highlighted. Some things will be interactive through web magic.  

We're going to do a toy version of restricted Hartree--Fock for understanding purposes. Basically `Hello World!` to H<sub>2</sub>.

---

## Rust 🦀

Right, I wore my trousers rolled and scuttled through the conceptual waves of [Rustlings](https://rustlings.rust-lang.org/). Time to put skimming into practice and build something with the borrow checker reminding me of any memory allocation or variable error.

Yoinking [@iggedi-ig-ig](https://github.com/iggedi-ig-ig)'s [basis set parser](https://github.com/iggedi-ig-ig/fock-rs/tree/master/basis_set) since I want to leverage the [Basis Set Exchange](https://www.basissetexchange.org/).


```toml
[dependencies]
basis_set = { git = "https://github.com/iggedi-ig-ig/fock-rs", package = "basis_set" }
```

```rust
use basis_set::BasisSet;
```


---

## Python 🐍

```python

import sys

print("Hello world!")


```

---

## Julia 🔴🟢🟣

```julia

println("Hello world!")
```

Julia is designed to hit sweet-spot of easy to write and performance for scientific code, so muich so that there's now a full production quality [Quantum Chemistry package written in Julia](https://doi.org/10.1021/acs.jctc.0c00337). 

---

Embedded Rust with `wasm-pack build --target web` and upload as a module with a `.js` file

Python load a `pyodide.js`. Will be slow 

Julia embed the HTML for a Pluto notebook with sliders. Then link to a JuliaHub with they want to modify the source code

---

Thank you for reading! 

