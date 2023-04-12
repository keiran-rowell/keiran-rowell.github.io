---
layout: post
author: keiran  
title: "Selecting an active space"
subtitle: "How to multiconfigurational without falling into despair"
category: guide 
tags: active-space CASSCF multiconfigurational electronic-structure
#image:
#  path: ../images/Jacobs_ladder_Goerigk_Grimme.jpg
---

*This post is adapted straight from my* [PhD Thesis](http://handle.unsw.edu.au/1959.4/65036)*, and deals with struggle of creating a workable active space for multiconfigurational calculations. 

Multiconfigurational methods are where the training wheels come off, you can no longer use a "black-box" combination of method and basis set -- you **have** to think about the chemical problem. There is therefore no right answer, but chemical intuition comes into play (what bonds break/form, which orbitals are populated?). Start with simple orbitals and build up. So, small basis sets, make sure it converges, then enlarge the basis set if needs must. Try to treat the "which orbitals?" and "how small a basis set can I get away with?" problems separately. I've also been told that calculating the cation (thus giving you "pulled in" orbitals) is another trick to get started.*

---

\chapter{CASSCF Calculations and MECI Searches}\label{ch:CAS_details}
In order to search for an optimised minimum energy conical intersection (MECI), a configuration where two electronic states are degenerate in energy, a multiconfigurational quantum chemistry method must be used. This involves optimising both the orbital coefficients, but unlike single-reference methods, also optimising the combinations of multiple Slater determinants; also known as configuration state functions (CSFs) in the language of multiconfigurational methods. The choice of an appropriate set of CSFs is crucial for a qualitatively correct description of the wavefunction.

While individual CSFs could be manually selected, one of the most common approaches is the complete active space (CAS) method where all possible configurations inside a selected orbital active space are treated. The self-consistent field (SCF) is used, and so the method at at this level of theory is known as CASSCF. The use of an active space removes the burden of choosing particular CSFs to include in the SCF optimisation, but requires the selection of appropriate active space orbitals which capture the chemical process of interest. Usually this includes any orbitals near the frontier orbitals, those involved in making and breaking bonds, the inclusion of correlated bonding and anti-bonding pairs, and any orbitals which are calculated to have incomplete occupation according to orbital population schemes.

\section{Generation of natural bond orbitals}
Selection of orbitals to include in the active space is more easily done if natural bond orbitals (NBOs) are used since they correspond to chemical intuition and are localised to the reactive space, while canonical orbitals are often too delocalised to be interpretable.

Minimal basis sets are easier to converge in a CASSCF calculation than large basis sets, and also aid in intrepretability. The starting point for all calculations was generation of an initial orbital population at the $S_1$ TS configuration, using NBOs at the HF/STO-3G level of theory. An example Gaussian input file to generate these NBOs is given in \autoref{code:save_NBOs} below. This process was also repeated if a large basis set, such as 6-31+G(d), was used.

\begin{listing}[!h]
\inputminted{bash}{code/print_NBOs.gjf}
\caption{Gaussian input file to save natural bond orbitals to a checkpoint file.}
\label{code:save_NBOs}
\end{listing}

The generated NBOs can also be examined in an external program (Chemcraft in this example). The Gaussian input file in \autoref{code:print_NBOs} shows the extra input at the bottom required to call on the NBO program to print the calculated natural bond orbitals to file.  These will be labelled FILE.$X$ where $X$ is 31--37. Chemcraft can open up FILE.31 directly, and should recognise the FILE.$X$ files for import. Chemcraft can then render NBOs from these files using the drop-down options: \texttt{Tools $\rightarrow$ Orbitals $\rightarrow$ Render molecular orbitals $\rightarrow$ NBOs}. Be aware: there is a reordering from the .log file and the .chk file, so only rely on the numbering in GaussView when identifying orbital indexes.

\begin{listing}[!h]
\inputminted{bash}{code/print_NBOs.gjf}
\caption{Gaussian input file to print NBOs for reading with an external program}
\label{code:print_NBOs}
\end{listing}

\section{Selection of the active space}
It is useful to check both the character of these NBOs from their density distribution, as well as their occupation value according to the NBO scheme. Any molecular orbitals which have occupations that differ significantly from the 0/2 value for virtual/occupied orbitals are likely candidates for inclusion in the active space.

The conical intersection of interest is between the $S_1$/$S_0$ states of the carbonyl. This conical intersection will be present near the vicinity of the transition state which involves a 1,5--H-shift from the carbonyl oxygen to the $\gamma$-hydrogen. Correlated pairs of bonding and anti-bonding orbitals should be included, for example if a \ch{C-H} $\sigma$ bonding orbital is included the corresponding \ch{C-H} $\sigma^{*}$ antibonding orbital should also be included. The oxygen $n$ orbital which interacts with the $\gamma$-hydrogen and also changes occupation in the excited state is crucial to include in active space, as well as the \ch{C=O} $\pi$ bonding and antibonding orbitals.

Additionally, since the photoexcited \ch{C=O} moiety abstracts a hydrogen atom to form a \ch{C-O-H} bond, the \ch{C-O} orbitals were found to be important for inclusion in the active space. This is particularly true when a STO-3G minimal basis set was used, which would deliver optimised \ch{C-O} bond lengths approximately 0.3 \AA\ larger than in the transition state structure. With large basis sets the \ch{C-O} bond length varied little from the transition state structure and hence the inclusion of corresponding orbitals was of less importance.

A reasonable (8,7) active space for typical saturated carbonyls includes:
\begin{itemize}
    \item \ch{C-O} $\sigma$ and $\sigma^{*}$ orbitals.
    \item \ch{C=O} $\pi$ and $\pi^{*}$ orbitals
    \item {O} $n$ orbital of the lone pair.
    \item $\gamma$\ch{C-H} $\sigma$ and $\sigma^{*}$ orbital.
 \end{itemize}

The NBOs which correspond to this active space are shown in the example of butanal in \ref{fig:NBO_butanal_active_space} at an isosuraface value of 0.1. While literature calculations use a (8,7) active space,\cite{Kletskii2014} a (10,8) active space that includes the alternate O $n$ oxygen-centred NBO was used as the largest active space. Structures computed from such CAS(10,8) calculations are reported in the main body of the thesis. 

\begin{figure}[!h]
\begin{minipage}{0.74\linewidth}
\begin{subfigure}[t]{0.32\linewidth}
    \centering
    \includegraphics[width=\linewidth]{fig/NBOs/butanal_NBO_C-O_sigma.jpg}
    \caption{\ch{C-O} $\sigma$}
    \label{fig:butanal_NBO_C-O_sigma}
\end{subfigure}\hfill
\begin{subfigure}[t]{0.32\linewidth}
    \centering
    \includegraphics[width=\linewidth]{fig/NBOs/butanal_NBO_C=O_pi.jpg}
    \caption{\ch{C=O} $\pi$}
    \label{fig:butanal_NBO_C=O_pi}
\end{subfigure}\hfill
\begin{subfigure}[t]{0.32\linewidth}
    \centering
    \includegraphics[width=\linewidth]{fig/NBOs/butanal_NBO_yC-H_sigma.jpg}
    \caption{$\gamma$\ch{C-H} $\sigma$}
    \label{fig:butanal_NBO_yC-H_sigma}
\end{subfigure}\hfill
\\
\begin{subfigure}[t]{0.32\linewidth}
    \centering
    \includegraphics[width=\linewidth]{fig/NBOs/butanal_NBO_C-O_sigma_star.jpg}
    \caption{\ch{C-O} $\sigma^{*}$}
    \label{fig:butanal_NBO_C-O_sigma*}
\end{subfigure}\hfill
\begin{subfigure}[t]{0.32\linewidth}
    \centering
    \includegraphics[width=\linewidth]{fig/NBOs/butanal_NBO_C=O_pi_star.jpg}
    \caption{\ch{C=O} $\pi^{*}$}
    \label{fig:butanal_NBO_C=O_pi*}
\end{subfigure}\hfill
\begin{subfigure}[t]{0.32\linewidth}
    \centering
    \includegraphics[width=\linewidth]{fig/NBOs/butanal_NBO_yC-H_sigma_star.jpg}
    \caption{$\gamma$\ch{C-H} $\sigma^{*}$}
    \label{fig:butanal_NBO_yC-H_sigma*}
\end{subfigure}\hfill
\end{minipage}
\begin{minipage}{0.24\linewidth}
\begin{subfigure}[t]{\linewidth}
    \centering
    \includegraphics[width=\linewidth]{fig/NBOs/butanal_NBO_O_n.jpg}
    \caption{\ch{O} $n$}
    \label{fig:butanal_NBO_O_n}
\end{subfigure}\hfill
\end{minipage}
\caption[Natural bond orbitals used in butanal CAS calculations.]{Natural bond orbitals for butanal, showing those typical for the active space of a CAS(8,7) calculation on a saturated carbonyl. CAS(10,8) active spaces include the other oxygen-centred NBO.}
\label{fig:NBO_butanal_active_space}
\end{figure}

For unsaturated species, it was found to be beneficial to also include the $\pi$ and $\pi^{*}$ orbitals of the point of unsaturation. A (12,10) active space is very computationally demanding, so for unsaturated species the (10,8) active space sized is preserved by removing the \ch{C-O} $\sigma$ and $\sigma^{*}$ NBOs, and replacing them with the $\pi$ and $\pi^{*}$ orbitals from the point of unsaturation, as illustrated in \ref{fig:NBO_2-oxobutanal_active_space}. 

\begin{figure}[!h]
\begin{subfigure}[t]{0.24\linewidth}
    \centering
    \includegraphics[width=\linewidth]{fig/NBOs/2-oxobutanal_NBO_O_n.jpg}
    \caption{O $n$}
    \label{fig:2-oxobutanal_NBO_O_n}
\end{subfigure}\hfill
\begin{subfigure}[t]{0.24\linewidth}
    \centering
    \includegraphics[width=\linewidth]{fig/NBOs/2-oxobutanal_NBO_C=O_1_pi.jpg}
    \caption{\ch{C=O} $\pi$}
    \label{fig:2-oxobutanal_C=O_1_pi}
\end{subfigure}\hfill
\begin{subfigure}[t]{0.24\linewidth}
    \centering
    \includegraphics[width=\linewidth]{fig/NBOs/2-oxobutanal_NBO_C=O_2_pi.jpg}
    \caption{Alternate \ch{C=O} $\pi$}
    \label{fig:2-oxobutanal_NBO_C=O_2_pi}
\end{subfigure}\hfill
\begin{subfigure}[t]{0.24\linewidth}
    \centering
    \includegraphics[width=\linewidth]{fig/NBOs/2-oxobutanal_NBO_yC-H_sigma.jpg}
    \caption{$\gamma$\ch{C-H} $\sigma$}
    \label{fig:2-oxbutanal_NBO_yC-H_sigma}
\end{subfigure}\hfill
\\
\begin{subfigure}[t]{0.24\linewidth}
    \centering
    \includegraphics[width=\linewidth]{fig/NBOs/2-oxobutanal_NBO_O_alt_n.jpg}
    \caption{Alternate O $n$}
    \label{fig:2-oxbutanal_NBO_alt_O_n}
\end{subfigure}\hfill
\begin{subfigure}[t]{0.24\linewidth}
    \centering
    \includegraphics[width=\linewidth]{fig/NBOs/2-oxobutanal_NBO_C=O_1_pi_star.jpg}
    \caption{\ch{C=O} $\pi^{*}$}
    \label{fig:2-oxobutanal_NBO_C=O_1_pi_star}
\end{subfigure}\hfill
\begin{subfigure}[t]{0.24\linewidth}
    \centering
    \includegraphics[width=\linewidth]{fig/NBOs/2-oxobutanal_NBO_C=O_2_pi_star.jpg}
    \caption{Alternate \ch{C=O} $\pi^{*}$}
    \label{fig:2-oxobutanal_NBO_C=O_2_pi_star}
\end{subfigure}\hfill
\begin{subfigure}[t]{0.24\linewidth}
    \centering
    \includegraphics[width=\linewidth]{fig/NBOs/2-oxobutanal_NBO_yC-H_sigma_star.jpg}
    \caption{$\gamma$\ch{C-H} $\sigma^{*}$}
    \label{fig:2-oxobutanal_NBO_yC-H_sigma_star}
\end{subfigure}\hfill
    \caption[Natural bond orbitals used in 2-oxobutanal CAS calculations.]{Natural bond orbitals for 2-oxobutanal, showing those typical for the active space of a CAS(10,8) calculation on an unsaturated carbonyl. In these carbonyls with a point of unsaturation the other $\pi$ and $\pi^{*}$ NBOs are included in favour of the \ch{C-O} $\sigma$ and $\sigma^{*}$ NBOs to keep the active space manageable.}
    \label{fig:NBO_2-oxobutanal_active_space}
\end{figure}

Once identified, these orbitals of interest need to be rotated into the active space. The orbitals which are considered in the active space are those nearest the HOMO/LUMO frontier according to the ($n$,$m$) active space chosen. The ($n$,$m$) nomenclature means enough occupied molecular orbitals to host $n$ electrons are treated as active. These are taken from the HOMO index and those sequentially below. The number of virtual orbitals in the active space is $m$ less the number of active occupied orbitals, and they are indexed from the LUMO and those sequentially above it.

\section{Performing CASSCF and MECI calculations}
The easiest way to perform this active space selection with the orbitals in the correct index is to interchange orbitals read in from the NBO checkpoint file. This process is illustrated in \autoref{code:CAS_S0} --- interchanging as an example orbitals 9 and 25, as well as 40 and 31. 

Note: before running \autoref{code:CAS_S0}, copy the checkpoint file containing NBOs from \autoref{code:save_NBOs} to have same name as the checkpoint filename used in \autoref{code:CAS_S0} so the CASSCF calculation can read in the correct NBOs. The molecular geometry does not need to be supplied in \autoref{code:CAS_S0} since it is read from the checkpoint file.

The \texttt{iop(5/7=$N$)} keyword sets the amount of CASSCF convergence cycles used. While this can be increased, a slow or difficult to converge CASSCF calculation is often indicative of a poor active space. In some large molecules convergence can be slow, but if the energy is seen to be monotonically decreasing with each cycle then simply increasing the amount of available cycles may be all that is needed. 

\begin{listing}[!h]
\inputminted{bash}{code/CAS_S0.gjf}
\caption{Gaussian input file to rotate orbitals into the active space and optimised the $S_0$ CASSCF wavefunction.}
\label{code:CAS_S0}
\end{listing}


If this CAS($n$,$m$) calculation converges on the $S_0$ state at configuration of the $S_1$ NTII TS geometry calculated by TD-DFT, then this  wavefunction is taken as a good initial guess for a beginning a conical intersection optimisation.

An example input file of running a minimum energy conical intersection (MECI) search with Gaussian is given in \autoref{code:CI_search} below. Again, the checkpoint file from a previous job must be copied to this checkpoint filename specified in the current job to read the orbitals, in this case from the converged CAS $S_0$ calculations. Note: in Gaussian 16 the state average weights must be included at the bottom of the input file, whereas Gaussian 09 does not need this extra input and defaults to the 0.5, 0.5 weighting between the upper and lower state of the same spin.

\begin{listing}[!h]
\inputminted{bash}{code/CI_search.gjf}
\caption{Gaussian input file for running a MECI search. }
\label{code:CI_search}
\end{listing}

The \texttt{iop(1/8=$N$)} keyword sets the maximum step size during the optimisation, and  generally needs to be decreased from its default value of $N = 30$ which corresponds to 0.3 Bohr. Since the $S_1$ Norrish Type II TS structure is taken as being close MECI a small step size is appropriate and avoids issues where the optimiser can overshoot the MECI several times if large step sizes are used. The maximum number of convergence cycles may again need to be increased through the use of the \texttt{iop(5/7=$N$)} keyword, however since an already converged $S_0$ CAS wavefunction is used as the initial guess the convergence during MECI searches tended to be well behaved, and convergence issues were often an indication that the geometry optimiser has strayed into a bad part of configuration space and a new guess geometry must be used. 

The $S_1$/$S_0$ state energy difference is reported in the log file as `\texttt{Energy difference=     $X$}' and this difference should be monitored, as well as the usual geometry convergence criteria of force and displacement values. If the energy difference, forces, or geometry begin to oscillate around a central zero value then decreasing the step size at this stage may improve the MECI search.


