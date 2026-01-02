---
layout: post
author: keiran  
title: "Hartree–Fock in Rust, Julia, and Python"
subtitle: "Quantum Chem's NextGen Lang Trifecta"
category: code
tags: Hartree-Fock Python Julia Rust code tutorial quantum-chemistry 
---

> 🧪 **Try it yourself**: [Interactive demos available→]({% post_url 2026-12-12-HF-interactive %})
>
> Run the H<sub>2</sub> Hartree-Fock calculations from this post directly in your browser.

---

[Program in C](https://youtu.be/tas0O586t80?si=H2HnFcVoS4tNqKB0) they said. It's good for you they said. [And it is!](https://youtu.be/hE7l6Adoiiw?si=Ourgha7DTfRy_Cer)
That is until you step outside the bounds of an array. Or dereference the wrong pointer to an array of pointers. Or, heaven forbid in this chatty age, want to do text processing.
C is *fast*, it allocates memory like machine code. But it's not the only game in town, and [not always the fastest](https://www.i-programmer.info/news/98-languages/15506-rust-fast-and-safe.html). 
C++ gives you a lot of powerful language features. But I don't write in it, I never took enterprise software engineering and I like to keep digital shotguns well away from my feet.

> "C makes it easy to shoot yourself in the foot; C++ makes it harder, but when you do it blows your whole leg off".

--- [Bjarne Stroustrup](https://www.stroustrup.com/quotes.html), developer of the C++ programming language

So let's reimplement the fundamental orbital energy optimiser, the basis for all [electronic structure theory methods]({% post_url 2023-04-12-compchem-methods-basics %}): Hartree--Fock.  <span style="color:#A9A9A9">(With deep debt to [QUACCS](https://quaccs.wordpress.com/))</span>

In with the new <span style="color:#A9A9A9">(apologies Formula Translation maintainence work)</span>; so for pedagogical/andragogical reasons, and to learn a couple of new languages, let's write the same algo in three languages:

- 🐍 `Python`: It's Python! It's everywhere. It's *readable*. It's not so bad as you would think because core Numerical Python is implemented in highly optimised C anyway. 
- 🔴🟢🟣 `Julia`: "[*as flexible as Python, as numerical as Matlab, as fast as Fortran, and as deep as Lisp.*](https://discourse.julialang.org/t/elevator-pitch/29457/8)". Designed *for* scientific computing. Well, what's not to like? It's REPL prompt is super nice, it's package manager doesn't make me prematurely age like Python does in my day job. And Just-In-Time compilation is *incredibly smart*. <span style="color:#A9A9A9">(I secretly think this is why observables are indeterminate until measured, but today we're strictly ["Shut up and calculate"](https://hsm.stackexchange.com/questions/3615/who-was-the-first-to-say-shut-up-and-calculate))</span> 
- 🦀 `Rust`: It's all the rage, faster than C, and very nicely gives you a talking to when it can see mistakes in the future. However, it's designed for deep systems programming. Quite likely overkill, but might give performance advantages and can be hosted on a site with WebAssembly.


With [WebAssembly](https://rust-lang.org/what/wasm/) and [Pluto notebooks](https://plutojl.org/) we can do quantum chemistry in our browser. Let's goooo--- 

---

The Hartree--Fock algorithm is the computational kernel for more accurate [electronic structure wavefunction methods]({% post_url 2023-04-12-compchem-methods-basics %}), where electron behaviour is improved by addition of either 'dynamic' electron correlation (mutual repulsion during motion) and 'static' correlation (fun stuff where a single arrangement of reference electron orbitals are insufficient). First we need to get a reasonable set of combined atomic orbitals for the resting state of a molecule. I'm using "pre-baked" basis-sets as really I want to focus on the algorithm (Roothaan--Hall eigenvalue finding) and coding it up.

So, we're starting with a set of atomic orbitals ($$\chi_{n}$$) (here, the minimal viable ones, the basis-set). We combine them to get some set of molecular orbitals ($$\phi_{i} = \sum\limits_{n}C_{ni}\chi_{n}$$) (MOs). 

If we take these electrons and capture their properties as spin--$$\frac{1}{2}$$ particles---kinetic energy, attraction to nuclei, electron--electron repulsions, change of sign upon indistinguishable particle exchange (Fermi stats)--- we get the Fock operator $$\hat{F}$$ to work with. Really, the Fock operator is related to the overlap of orbital basis set vectors ($${S}$$), and we can use an algorithm to optimise the co-efficients ($${C}$$) of these orbitals to lower the orbital energies ($$\epsilon$$)

So we have the Roothan--Hall matrix optimisation problem of finding the co-efficients that lowers the molecular orbital energies, which is guaranteed to be the closest to ground-state reality for HF (the Variational Principle).

$$\mathbf{FC} =  \mathbf{SC}\epsilon$$ 

Right, enough notation. Let's set up an engine that finds the energy eigenvalues ($$\epsilon$$) given some input orbitals, and then uses and optimisation algorithm to feed the output co-efficients back in to iteratively refind until converge. Yielding a set of one-electron orbitals solved in "self-consistent field" with respect to the other electrons. Time to code. 

 
> Code snippets will be as quotes. Blocks will be syntax highlighted. Some things will be interactive through web magic. Those are in a later [post]() 

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
    R: Array{Float64}((1, 3)) [0.0 0.0 1.4]
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

## The overlap integral (S) 

So the core of part the algorithm is computing the **overlap matrix** $$\mathbf{S}$$ between two basis functions in space.

$$S_{ij} = \langle \chi_i | \chi_j \rangle = \int \chi_i^*(\mathbf{r}) \chi_j(\mathbf{r}) \, d\mathbf{r}$$

We'll write a function that computes the overlap of two basis functions, working on the primitives with their exponents (α, β).

🐍
`def compute_S_primitive(alpha, beta, R_A, R_B)`

🔴🟢🟣
`function compute_S_primitive(α::Float64, β::Float64, R_A::Vector{Float64}, R_B::Vector{Float64})`

🦀
`let S = overlap_integral(&basis1, &basis2);`

We have two hydrogen atoms with a minimal basis, so we should get a 2x2 matrix to inspect.

$$\mathbf{S} = \begin{bmatrix}
\langle \chi_1 | \chi_1 \rangle & \langle \chi_1 | \chi_2 \rangle \\
\langle \chi_2 | \chi_1 \rangle & \langle \chi_2 | \chi_2 \rangle
\end{bmatrix}$$

A basis function completely overlaps with itself, so we get one on the diagonals, and the overlap values ($$S_{ij}$$) on the off-diagonals depend on your basis set and molecular geometry. 

$$\mathbf{S} = \begin{bmatrix}
1 & S_{12} \\
S_{21} & 1
\end{bmatrix}$$

The self-consistent field cycles will optimise the co-efficients for how your orbitals combine within this overlap.


With two s-orbital Gaussian *primitives* the overlap integral is:

$$S = \left(\frac{\pi}{\alpha + \beta}\right)^{3/2} \exp\left(-\frac{\alpha\beta}{\alpha+\beta}|\mathbf{R}_A - \mathbf{R}_B|^2\right)$$

🐍
```python
S_prim = (np.pi / (alpha + beta))**(3/2) * np.exp(-alpha * beta / (alpha + beta) * np.sum((R_A - R_B)**2))
```
🔴🟢🟣 <span style="color:#A9A9A9">(the `.` operator means apply to each *element* in an array independently)</span>
```julia
S_prim = (π / (α + β))^(3/2) * exp(-(α * β / (α + β)) * sum((R_A .- R_B).^2))
```
🦀
```rust
let dist_sq: f64 = (0..3) //summing over X,Y,Z indices
    .map(|i| (r_a[i] - r_b[i]).powi(2))
    .sum();
let S_prim = (std::f64::consts::PI / (alpha + beta)).powf(1.5) 
    * (-alpha * beta / (alpha + beta) * dist_sq).exp();
```

The actual `overlap_integral` function when working with a real contracted basis set will involved summing the primitives in the basis set, weighted by contraction co-efficients and normalised. 

---

## Operator matrices setup

### Denisty matrix (D)
To kickstart our engine we need an intial electron density matrix ($$\mathbf{D}$$). For a toy system it's actually okay to start with zero density everywhere (or the identity matrix). 

Though for any real molecular system choice of a good guess is important for convergence. For difficult to converge cases, feeding in the results of a simpler model chemistry will help start need a convergent minimum.

🐍
```python
D = np.zeros((n_basis, n_basis))
```
🔴🟢🟣
```julia
D = zeros(n_basis, n_basis)
```
🦀
```rust
TODO: UPDATE
let mut d = Array2::<f64>::zeros((n_basis, n_basis));
```

### Fock operator (F)

For teaching purposes we're going to skip the electron-electron repulsion integrals (ERIs) that are the bulk of the computational cost and code complexity.
In this way our *toy* Fock matrix ($$\mathbf{F}$$) is just the core Hamiltonian ($$\mathbf{F}$$--- the total energy of forces acting on our one-electron core). This is really just our electrons' kinetic energies ($$\mathbf{T}$$) and their attractive potential energy to the nuceli ($$\mathbf{V}^{\text{nuc}}$$)

$$\mathbf{F} = \mathbf{H}^{\text{core}} = \mathbf{T} + \mathbf{V}^{\text{nuc}}$$

### Kinetic energy operator (T)

The electron kinetic energy is the momentum taken in all directions ($$\nabla$$):
$$\hat{T} = -\frac{1}{2}\nabla^2$$

When evaluating between two basis functions:
$$T_{\mu\nu} = \left\langle \chi_\mu \left| -\frac{1}{2}\nabla^2 \right| \chi_\nu \right\rangle$$

Taking the result from Szabo & Ostlund *"Modern Quantum Chemistry"* Appendix A as I'm not a physicist. Note the relationship to $$S$$:

$$T = \alpha\beta\left[\frac{3}{\alpha+\beta} - \frac{2(\alpha\beta)}{(\alpha+\beta)^2}|\mathbf{R}_A - \mathbf{R}_B|^2\right] S$$

🐍
```python
reduced_exp = alpha * beta / (alpha + beta)
T_prim = reduced_exp * (3 - 2 * reduced_exp * np.sum((R_A - R_B)**2)) * S_prim
```
🔴🟢🟣
```julia
reduced_exp = α * β / (α + β)
T_prim = reduced_exp * (3 - 2 * reduced_exp * sum((R_A .- R_B).^2)) * S_prim
```
🦀
```
let reduced_exp = alpha * beta / (alpha + beta);
let T_prim = reduced_exp * (3.0 - 2.0 * reduced_exp * dist_sq) * S_prim;
```

### Nuclear attraction potential (V)
We invoke the Born-Oppenheimer approximation that electron motion occurs on much faster timescale than nuclear re-arrangement (can also think of this in terms of different decoupled energy scales). So the nuclei are effectively *fixed* in place.

$$\hat{V}^{\text{nuc}}_A = -\frac{Z_A}{|\mathbf{r} - \mathbf{R}_A|}$$

$$V^{\text{nuc}}_{\mu\nu} = -\left\langle \chi_\mu \left| \frac{1}{|\mathbf{r} - \mathbf{R}_1|} \right| \chi_\nu \right\rangle - \left\langle \chi_\mu \left| \frac{1}{|\mathbf{r} - \mathbf{R}_2|} \right| \chi_\nu \right\rangle$$

The nuclear attraction integrals involve special functions that are beyond our scope here. They're implement in `integrals.[py/jl/rs]` since 1/R wasn't showing good behaviour even for a toy system. I'm just going to mention the function header for this guide, those curious can refer to the code generated from a reference.  

🐍
```python
def compute_V_nuc_primitive(alpha, beta, R_A, R_B, R_nuc):
```
🔴🟢🟣
```julia
function compute_V_nuc_primitive(α::Float64, β::Float64, R_A::Vector{Float64}, R_B::Vector{Float64}, R_nuc::Vector{Float64}) 
```
🦀
```
TBD
```


### Electron Repulsion Integrals (ERIs)

The most demanding part of the Hartree--Fock calculation, both computational and mathematically. I've farmed them out to `integrals.py` to not break the logic flow of SCF. This is where I've put the overlap and kinetic energy integrals as well.  

The electron-electron repulsion matrix ($$\mathbf{G}$$) captures both the Coloumbic repulsions between negative charges ($$\mathbf{J}$$) and the quantum effect of change of wavefunction sign upon exchange of two particles ($$\mathbf{K}$$)

$$\mathbf{G}[\mathbf{D}] = \mathbf{J}[\mathbf{D}] - \mathbf{K}[\mathbf{D}]$$

Refer to `integrals.[py/jl/rs]`, which I've just generated from a reference, if you want more details. 

🐍
```python
G = build_G_matrix(D, ERIs)
F = T + V_nuc + G
```
🔴🟢🟣
```julia
G = build_G_matrix(D, ERIs)
F = T + V_nuc + G
```
## The self-consistent field (SCF) loop

Recall this is an iterative eigenvalue finding problem
$$\mathbf{FC} = \epsilon\mathbf{SC}$$

To that that we need to do some orthogonalisation
$$ \mathbf{X} = \mathbf{S}^{-\frac{1}{2}} $$

Use the transpose of the orthogonalisation matrix ($$\mathbf{X}^{T}$$) to transform the Fock operator into the new basis
$$ \mathbf{F}' = \mathbf{X}^{T}\mathbf{F}\mathbf{X} $$

Solve for the eignevalues of the co-efficient matrix
$$ \mathbf{F}'\mathbf{C}' = \mathbf{C}'\epsilon $$

Update the new co-efficient matrix into original basis
$$ \mathbf{C} = \mathbf{X}\mathbf{C}' $$

🐍
```python
s_eigvals, s_eigvecs = np.linalg.eigh(S)
X = s_eigvecs @ np.diag(s_eigvals**(-0.5)) @ s_eigvecs.T

F_prime = X.T @ F @ X

epsilon, C_prime = np.linalg.eigh(F_prime)

C = X @ C_prime
```
🔴🟢🟣
```julia
using LinearAlgebra

s_eigvals, s_eigvecs = eigen(Symmetric(S))
clean_eigvals = max.(s_eigvals, 1e-15) # avoid inverting numerical noise
X = s_eigvecs * Diagonal(clean_eigvals .^ (-0.5)) * s_eigvecs'

F′ = X' * F * X
ϵ, C′ = eigen(Symmetric(F′))
C = X * C′
```
🦀
```rust
use ndarray_linalg::*;

let (s_eigvals, s_eigvecs) = s.eigh(UPLO::Lower)?;
let s_inv_sqrt = s_eigvecs.dot(&Array2::from_diag(&s_eigvals.mapv(|x| x.powf(-0.5)))).dot(&s_eigvecs.t());

let f_prime = s_inv_sqrt.t().dot(&f).dot(&s_inv_sqrt);

let (epsilon, c_prime) = f_prime.eigh(UPLO::Lower)?;

let c = s_inv_sqrt.dot(&c_prime);
```

Time to update the density matrix using these new co-efficients. This is H<sub>2</sub> in restricted Hartree--Fock so only one occupied orbital to deal with.

$$D_{\mu\nu} = 2\sum_{i}^{\text{occ}} C_{\mu i} C_{\nu i}$$

🐍
```python
num_occ = num_electrons // 2 
D_new = 2 * C[:, :num_occ] @ C[:, :num_occ].T
```
🔴🟢🟣
```julia
num_occ = num_electrons ÷ 2 
D_new = 2 * C[:, 1:num_occ] * C[:, 1:num_occ]'
```
🦀
```rust
let n_occ = n_electrons / 2; 
let c_occ = c.slice(s![.., 0..n_occ]);
let d_new = 2.0 * c_occ.dot(&c_occ.t());
```
### Energy convergence check

We can calculate the energy from summing enetries in the Fock operator and core Hamiltonian

$$E = \frac{1}{2}\text{Tr}[\mathbf{D}(\mathbf{H}^{\text{core}} + \mathbf{F})]$$

Then it's just the matter of checking that the energy hasn't changed between each cycle, to some tolerance

$$\Delta E = |E_{\text{new}} - E_{\text{old}}| < \epsilon_{\text{tol}}$$

🐍
```python
E_new = 0.5 * np.trace(D_new @ (H_core + F))

delta_E = abs(E_new - E_old)
if delta_E < epsilon_tol:
    converged = True
    print(f"Converged! Final energy: {E_new:.6f} Ha")
else:
    E_old = E_new
    D = D_new
```
🔴🟢🟣
```julia
E_new = 0.5 * tr(D_new * (H_core + F))

ΔE = abs(E_new - E_old)
if ΔE < ε_tol
    converged = true
    println("Converged! Final energy: $E_new Ha")
else
    E_old = E_new
    D = D_new
end
```
🦀
```
let e_new = 0.5 * (&d_new * &(&h_core + &f)).trace().unwrap();

let delta_e = (e_new - e_old).abs();
if delta_e < epsilon_tol {
    converged = true;
    println!("Converged! Final energy: {:.6} Ha", e_new);
} else {
    e_old = e_new;
    d = d_new;
}
```

We wrap the above in a loop with a maximum number of iterations and we're ready!

---
# Performance comparison

Obviously solving a fake H<sub>2</sub> is a terrible comparison for the code performance doing real chemistry. Nevertheless..

---

## Non execution speed stuff

### Lines of code
### Ease of development
### Readability
### Any other pains

---
# Creating web content
---
Embedded Rust with `wasm-pack build --target web` and upload as a module with a `.js` file

Python load a `pyodide.js`. Will be slow 

`Julia` 🔴🟢🟣: there's a live Pluto notebook with H<sub>2</sub> sliders [here](https://pluto.land/n/lg6ry63f).

Julia is designed to hit sweet-spot of easy to write and performance for scientific code, so muich so that there's now a full production quality [Quantum Chemistry package written in Julia](https://doi.org/10.1021/acs.jctc.0c00337). 

The sliders will be of R (maybe 0.25-1.5 A), so you can see the off-diagonal elements of S change, and the basis sets chosen from a dropdown. Then hit 'run' and watch the SCF cycles converge.

Have all 2x2 S matrix elements displayed. Plot the SCF cycles

---

## Related web resources

- 🐍 [Python version](/interactive/hf-python/index.html) - Run with Pyodide
- 🔴🟢🟣 [Julia version](/interactive/hf-julia/index.html) - Try it in your browser in a Pluto notebook
- 🦀 [Rust version](/interactive/hf-rust/index.html) - WebAssembly performance
- 💻 [Source Code](https://github.com/keiran-rowell/hartee-fock) - All implementations

