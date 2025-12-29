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

- 🐍 `Python`: It's Python! It's everywhere. It's *readable*. It's not so bad as you would think because core Numerical Python is implemented in highly optimised C anyway. 
- 🔴🟢🟣 `Julia`: "[*as flexible as Python, as numerical as Matlab, as fast as Fortran, and as deep as Lisp.*](https://discourse.julialang.org/t/elevator-pitch/29457/8)". Designed *for* scientific computing. Well, what's not to like? It's REPL prompt is super nice, it's package manager doesn't make me prematurely age like Python does in my day job. And Just-In-Time compilation is *incredibly smart*. <span style="color:#A9A9A9">(I secretly think this is why observables are indeterminate until measured, but today we're strictly ["Shut up and calculate"](https://hsm.stackexchange.com/questions/3615/who-was-the-first-to-say-shut-up-and-calculate))</span> 
- 🦀 `Rust`: It's all the rage, faster than C, and very nicely gives you a talking to when it can see mistakes in the future.

With [WebAssembly](https://rust-lang.org/what/wasm/) and [Pluto notebooks](https://plutojl.org/) we can do quantum chemistry in our browser. Let's goooo--- 

---

The Hartree--Fock algorithm is the computational kernel for more accurate [electronic structure wavefunction methods]({% post_url 2023-04-12-compchem-methods-basics %}), where electron behaviour is improved by addition of either 'dynamic' electron correlation (mutual repulsion during motion) and 'static' correlation (fun stuff where a single arrangement of reference electron orbitals are insufficient). First we need to get a reasonable set of combined atomic orbitals for the resting state of a molecule. I'm using "pre-baked" basis-sets as really I want to focus on the algorithm (Roothaan--Hall eigenvalue finding) and coding it up.

So, we're starting with a set of atomic orbitals ($$\chi_{n}$$) (here, the minimal viable ones, the basis-set). We combine them to get some set of molecular orbitals ($$\phi_{i} = \sum\limits_{n}C_{ni}\chi_{n}$$) (MOs). 

If we take these electrons and capture their properties as spin--$$\frac{1}{2}$$ particles---kinetic energy, attraction to nuclei, electron--electron repulsions, change of sign upon indistinguishable particle exchange (Fermi stats)--- we get the Fock operator $$\hat{F}$$ to work with. Really, the Fock operator is related to the overlap of orbital basis set vectors ($${S}$$), and we can use an algorithm to optimise the co-efficients ($${C}$$) of these orbitals to lower the orbital energies ($$\epsilon$$)

So we have the Roothan--Hall matrix optimisation problem of finding the co-efficients that lowers the molecular orbital energies, which is guaranteed to be the closest to ground-state reality for HF (the Variational Principle).

$$\mathbf{FC} =  \epsilon \mathbf{SC}$$ 

Right, enough notation. Let's set up an engine that finds the energy eigenvalues ($$\epsilon$$) given some input orbitals, and then uses and optimisation algorithm to feed the output co-efficients back in to iteratively refind until converge. Yielding a set of one-electron orbitals solved in "self-consistent field" with respect to the other electrons. Time to code. 

 
> Code snippets will be as quotes. Blocks will be syntax highlighted. Some things will be interactive through web magic.  

We're going to do a toy version of restricted Hartree--Fock for understanding purposes. 
Basically saying `Hello World!` to H<sub>2</sub>.

---

# Basis Sets

---
## Python 🐍

Using [@bennyp](https://github.com/bennybp) and [@susilehtola](https://github.com/susilehtola)'s [`basis_set_exchange`](https://molssi-bse.github.io/basis_set_exchange/usage.html#) library provied for MolSSI (the Molecular Sciences Software Institute). 

```python
pip install basis_set_exchange

import basis_set_exchange
sto3g_orca_fmt =  basis_set_exchange.get_basis('STO-3G', fmt='ORCA', header=False)
print(sto3g_orca_fmt)
```

```
$DATA

HYDROGEN
S   3
1         0.3425250914E+01       0.1543289673E+00
2         0.6239137298E+00       0.5353281423E+00
3         0.1688554040E+00       0.4446345422E+00
```
Looking good!

---

## Julia 🔴🟢🟣

Using [@Leticia-maria](https://github.com/Leticia-maria)'s [BasisSets.jl](https://github.com/HartreeFoca/BasisSets.jl) Basis Set Exchange parser.

```julia
using Pkg
Pkg.add("BasisSets")
using BasisSets
```

Create a `H2.xyz` with 0.74 Å / 1.4 Bohr seperation on the Z-axis. 
```
2

H 0.000000 0.000000 0.000000
H 0.000000 0.000000 1.400000
```

Check a minimal H<sub>2</sub> minimal basis set.

<span style="color:#A9A9A9">The README omits the intermediate molecule() function you can find by running names(BasisSets)</span>

```julia
h2_mol = molecule("./H2.xyz")
h2_sto3g = parsebasis(h2_mol, "STO-3g")
```

Inspect with `dump(h2_sto3g)`
```
Array{BasisSets.GaussianBasisSet}((2,))
  1: BasisSets.GaussianBasisSet
    R: Array{Float64}((1, 3)) [0.0 0.0 0.0]
    α: Array{Float64}((1, 3)) [3.42525091 0.62391373 0.1688554]
    d: Array{Float64}((1, 3)) [0.15432897 0.53532814 0.44463454]
    N: Array{Float64}((1, 3)) [1.794441832218435 0.5003264923314032 0.18773545851092535]
    size: Int64 3
    ℓ: Int64 0
    m: Int64 0
    n: Int64 0
  2: BasisSets.GaussianBasisSet
    R: Array{Float64}((1, 3)) [0.0 0.0 0.74]
    α: Array{Float64}((1, 3)) [3.42525091 0.62391373 0.1688554]
    d: Array{Float64}((1, 3)) [0.15432897 0.53532814 0.44463454]
    N: Array{Float64}((1, 3)) [1.794441832218435 0.5003264923314032 0.18773545851092535]
    size: Int64 3
    ℓ: Int64 0
    m: Int64 0
    n: Int64 0
```
With symbols, neat!

---

## Rust 🦀

Right, I wore my trousers rolled and scuttled through the conceptual waves of [Rustlings](https://rustlings.rust-lang.org/). Time to put skimming into practice and build something with the borrow checker reminding me of any memory allocation or variable error.

Yoinking [@iggedi-ig-ig](https://github.com/iggedi-ig-ig)'s [basis set parser](https://github.com/iggedi-ig-ig/fock-rs/tree/master/basis_set) since I want to leverage the [Basis Set Exchange](https://www.basissetexchange.org/).

Start project with `cargo new h2_hf_rust`

Download the `STO-3G` basis set file and save it within the project.

`wget -O sto-3g-h.json "https://www.basissetexchange.org/api/basis/sto-3g/format/json/?version=1&elements=1"` 

Add the basis set package to the `Cargo.toml` dependency listing, and the json parsing library
```toml
[dependencies]
basis_set = { git = "https://github.com/iggedi-ig-ig/fock-rs", package = "basis_set" }
serde_json = "1.0"
```

Test out BasisSet library function in `src/main.rs`
```rust
use basis_set::BasisSet;
use std::fs;

fn main() {
    let json = fs::read_to_string("sto-3g-h.json").unwrap();
    let basis: BasisSet = serde_json::from_str(&json).unwrap();

    println!("Loaded basis set: {} ({})", basis.name, basis.description);
    println!("\nFull details:\n{:#?}", basis);
}

```

And now run the project with `cargo run`

```
Full basis set details:
BasisSet {
...
                    exponents: [
                        "0.3425250914E+01",
                        "0.6239137298E+00",
                        "0.1688554040E+00",
                    ],
                    coefficients: [
                        [
                            "0.1543289673E+00",
                            "0.5353281423E+00",
                            "0.4446345422E+00",
...
    family: SlaterType,
    description: "STO-3G Minimal Basis (3 functions/AO)",
    role: "orbital",
    name: "STO-3G",
}
```
We have hydrogen's STO-3G basis!

---

# Hartree--Fock

---

TODO

---
# Web content
---
Embedded Rust with `wasm-pack build --target web` and upload as a module with a `.js` file

Python load a `pyodide.js`. Will be slow 

Julia embed the HTML for a Pluto notebook with sliders. Then link to a JuliaHub with they want to modify the source code

Julia is designed to hit sweet-spot of easy to write and performance for scientific code, so muich so that there's now a full production quality [Quantum Chemistry package written in Julia](https://doi.org/10.1021/acs.jctc.0c00337). 

---

Thank you for reading! 

