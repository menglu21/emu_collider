#!/usr/bin/env python

import sys

import ROOT

try:
  input = raw_input
except:
  pass

sig_xs = 0.1917
bkg_xs = 0.1416

if len(sys.argv) < 3:
  print(" Usage: emu_collider.py input_file1 input_file2")
  sys.exit(1)

ROOT.gSystem.Load("libDelphes")

try:
  ROOT.gInterpreter.Declare('#include "classes/DelphesClasses.h"')
  ROOT.gInterpreter.Declare('#include "external/ExRootAnalysis/ExRootTreeReader.h"')
except:
  pass

inputFile1 = sys.argv[1]
inputFile2 = sys.argv[2]

# Create chain of root trees
chain = ROOT.TChain("Delphes")
chain.Add(inputFile1)
event_cout_sig=0
event_cout_bkg=0
# Create object of class ExRootTreeReader
treeReader_sig = ROOT.ExRootTreeReader(chain)
numberOfEntries_sig = treeReader_sig.GetEntries()
weight_sig = sig_xs/numberOfEntries_sig
# Get pointers to branches used in this analysis
branchJet_sig = treeReader_sig.UseBranch("Jet")
branchElectron_sig = treeReader_sig.UseBranch("Electron")
branchMuon_sig = treeReader_sig.UseBranch("Muon")
branchMET_sig = treeReader_sig.UseBranch("MissingET")

# Book histograms
hist_sigJet1PT = ROOT.TH1F("signal jet1_pt", "jet1 P_{T}", 20, 0.0, 200.0)
hist_sigJet1PT.SetStats(0)
hist_sigJet1PT.Sumw2()
hist_sigJet1PT.GetXaxis().SetTitle('leading bjet pT [GeV]')
hist_sigJet1PT.GetYaxis().SetTitle('a.u.')
hist_sigJet2PT = ROOT.TH1F("signal jet2_pt", "jet2 P_{T}", 20, 0.0, 200.0)
hist_sigJet2PT.SetStats(0)
hist_sigJet2PT.Sumw2()
hist_sigJet2PT.GetXaxis().SetTitle('subleading bjet pT [GeV]')
hist_sigJet2PT.GetYaxis().SetTitle('a.u.')
hist_sigMass = ROOT.TH1F("signal mjj", "M_{b1b2}", 20, 80.0, 160.0)
hist_sigMass.SetStats(0)
hist_sigMass.Sumw2()
hist_sigMass.GetXaxis().SetTitle('Mbb [GeV]')
hist_sigMass.GetYaxis().SetTitle('a.u.')
hist_sigMET = ROOT.TH1F("signal MET", "MET", 20, 0.0, 100.0)
hist_sigMET.SetStats(0)
hist_sigMET.Sumw2()
hist_sigMET.GetXaxis().SetTitle('MET [GeV]')
hist_sigMET.GetYaxis().SetTitle('a.u.')

hist_bkgJet1PT = ROOT.TH1F("bkg jet1_pt", "jet1 P_{T}", 20, 0.0, 200.0)
hist_bkgJet1PT.SetStats(0)
hist_bkgJet1PT.Sumw2()
hist_bkgJet2PT = ROOT.TH1F("bkg jet2_pt", "jet2 P_{T}", 20, 0.0, 200.0)
hist_bkgJet2PT.SetStats(0)
hist_bkgJet2PT.Sumw2()
hist_bkgMass = ROOT.TH1F("bkg mjj", "M_{inv}(j_{1},j_{2})", 20, 80.0, 160.0)
hist_bkgMass.SetStats(0)
hist_bkgMass.Sumw2()
hist_bkgMET = ROOT.TH1F("bkg MET", "MET", 20, 0.0, 100.0)
hist_bkgMET.SetStats(0)
hist_bkgMET.Sumw2()

Jet1 = ROOT.TLorentzVector()
Jet2 = ROOT.TLorentzVector()
Jet1_bkg = ROOT.TLorentzVector()
Jet2_bkg = ROOT.TLorentzVector()

# Loop over all events
for entry in range(0, numberOfEntries_sig):
  if entry%1000==0: 
    print('processing ', entry)
  # Load selected branches with data from specified event
  treeReader_sig.ReadEntry(entry)
  Jet1.SetPtEtaPhiM(0,0,0,0)
  Jet2.SetPtEtaPhiM(0,0,0,0)

  # If event contains at least 1 jet
  if branchJet_sig.GetEntries() !=2:continue
    # Take first jet
  jet1 = branchJet_sig.At(0)
  jet2 = branchJet_sig.At(1)
  Jet1.SetPtEtaPhiM(jet1.PT,jet1.Eta,jet1.Phi,jet1.Mass)
  Jet2.SetPtEtaPhiM(jet2.PT,jet2.Eta,jet2.Phi,jet2.Mass)

  if jet1.BTag!=1 or jet2.BTag!=1 or jet1.Eta>0 or jet1.Eta<-2.5 or jet2.Eta>0 or jet2.Eta<-2.5 or jet1.PT<30 or jet2.PT<30:
      continue
  if (Jet1+Jet2).M()>150 or (Jet1+Jet2).M()<100:
      continue
  event_cout_sig +=1
  # Plot jet transverse momentum
  hist_sigJet1PT.Fill(jet1.PT,weight_sig)
  hist_sigJet2PT.Fill(jet2.PT,weight_sig)
  hist_sigMass.Fill((Jet1+Jet2).M(),weight_sig)
  met = branchMET_sig.At(0)
  hist_sigMET.Fill(met.MET,weight_sig)

print 'sig event number:', event_cout_sig
chain.Add(inputFile2)

# Create object of class ExRootTreeReader
treeReader_bkg = ROOT.ExRootTreeReader(chain)
numberOfEntries_bkg = treeReader_bkg.GetEntries()
weight_bkg = bkg_xs/numberOfEntries_bkg
# Get pointers to branches used in this analysis
branchJet_bkg = treeReader_bkg.UseBranch("Jet")
branchElectron_bkg= treeReader_bkg.UseBranch("Electron")
branchMuon_bkg = treeReader_bkg.UseBranch("Muon")
branchMET_bkg = treeReader_bkg.UseBranch("MissingET")

# Loop over all events
for entry in range(numberOfEntries_sig, numberOfEntries_bkg):
  if entry%1000==0:
    print('processing ', entry)
  # Load selected branches with data from specified event
  treeReader_bkg.ReadEntry(entry)
  Jet1_bkg.SetPtEtaPhiM(0,0,0,0)
  Jet2_bkg.SetPtEtaPhiM(0,0,0,0)

  # If event contains at least 1 jet
  if branchJet_bkg.GetEntries() !=2:continue
    # Take first jet
  jet1_bkg = branchJet_bkg.At(0)
  jet2_bkg = branchJet_bkg.At(1)
  Jet1_bkg.SetPtEtaPhiM(jet1_bkg.PT,jet1_bkg.Eta,jet1_bkg.Phi,jet1_bkg.Mass)
  Jet2_bkg.SetPtEtaPhiM(jet2_bkg.PT,jet2_bkg.Eta,jet2_bkg.Phi,jet2_bkg.Mass)

  if jet1_bkg.BTag!=1 or jet2_bkg.BTag!=1 or jet1_bkg.Eta>0 or jet1_bkg.Eta<-2.5 or jet2_bkg.Eta>0 or jet2_bkg.Eta<-2.5 or jet1_bkg.PT<30 or jet2_bkg.PT<30:
      continue
  if (Jet1_bkg+Jet2_bkg).M()>150 or (Jet1_bkg+Jet2_bkg).M()<100:
      continue
  event_cout_bkg +=1
  # Plot jet transverse momentum
  hist_bkgJet1PT.Fill(jet1_bkg.PT,weight_bkg)
  hist_bkgJet2PT.Fill(jet2_bkg.PT,weight_bkg)
  hist_bkgMass.Fill((Jet1_bkg+Jet2_bkg).M(),weight_bkg)

  met_bkg = branchMET_bkg.At(0)
  hist_bkgMET.Fill(met_bkg.MET,weight_bkg)

print 'bkg event number:',event_cout_bkg

c1= ROOT.TCanvas("j1pt","j1pt",800,600)
#c1.SetLogy()
c2= ROOT.TCanvas("j2pt","j2pt",800,600)
#c2.SetLogy()
c3= ROOT.TCanvas("mjj","mjj",800,600)
#c3.SetLogy()
c4= ROOT.TCanvas("MET","MET",800,600)
#c4.SetLogy()

l1 = ROOT.TLegend(0.7,0.75,0.9,0.9)
l2 = ROOT.TLegend(0.7,0.75,0.9,0.9)
l3 = ROOT.TLegend(0.7,0.75,0.9,0.9)
l4 = ROOT.TLegend(0.7,0.75,0.9,0.9)

c1.cd()
hist_sigJet1PT.SetLineColor(ROOT.kRed)
hist_sigJet1PT.Draw('pe')
hist_bkgJet1PT.SetLineColor(ROOT.kBlue)
hist_bkgJet1PT.Draw('pe same')
l1.AddEntry(hist_sigJet1PT,'hbb leading bjet')
l1.AddEntry(hist_bkgJet1PT,'zbb leading bjet')
l1.Draw()
c1.SaveAs('Ana_meng/b1pt.png')

c2.cd()
hist_sigJet2PT.SetLineColor(ROOT.kRed)
hist_sigJet2PT.Draw('pe')
hist_bkgJet2PT.SetLineColor(ROOT.kBlue)
hist_bkgJet2PT.Draw('pe same')
l2.AddEntry(hist_sigJet2PT,'hbb subleading bjet')
l2.AddEntry(hist_bkgJet2PT,'zbb subleading bjet')
l2.Draw()
c2.SaveAs('Ana_meng/b2pt.png')

c3.cd()
hist_sigMass.SetLineColor(ROOT.kRed)
hist_sigMass.Draw('pe')
hist_bkgMass.SetLineColor(ROOT.kBlue)
hist_bkgMass.Draw('pe same')
l3.AddEntry(hist_sigMass,'hbb invariant jet mass')
l3.AddEntry(hist_bkgMass,'zbb invariant jet mass')
l3.Draw()
c3.SaveAs('Ana_meng/mbb.png')

c4.cd()
hist_sigMET.SetLineColor(ROOT.kRed)
hist_sigMET.Draw('pe')
hist_bkgMET.SetLineColor(ROOT.kBlue)
hist_bkgMET.Draw('pe same')
l4.AddEntry(hist_sigMET,'hbb MET')
l4.AddEntry(hist_bkgMET,'zbb MET')
l4.Draw()
c4.SaveAs('Ana_meng/met.png')
