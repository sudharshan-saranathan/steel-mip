D=152.2
bof=0.51*D; eaf=0.49*D; cd=0.902*eaf; ng=eaf-cd
hm=1.1*bof*(1-0.09); sint=1.15*hm; coke=0.53*hm; cc=1.47*coke; pci=0.15*hm
pel_bf=0.35*hm
dri_c=1.1*cd*(1-0.382); dri_n=1.1*ng*(1-0.13)
lime_bf=0.04*sint+0.025*hm+0.075*bof; lime_eaf=0.06*eaf
s1 = cc*2.79+pci*2.756+dri_c*2.64+0.01*eaf*2.64+dri_n*0.35*2.75+(lime_bf+lime_eaf)*0.44+0.003*eaf*6
# power (kWh -> MWh per t => Mt*kWh = GWh)
pw = 75*coke+50*sint+55*hm+174*bof+217*dri_c+120*dri_n+200*(pel_bf+1.5*dri_c+1.5*dri_n)+664*eaf
rec = 80*coke+30*sint+35*hm
grid=(pw-rec)  # GWh*1e-3... Mt*kWh/t = 1e9 kWh
s2 = grid*0.886e-3   # Mt CO2 (Mt*kWh/t * tCO2/kWh)
print(f"coking coal {cc:.1f} Mt, coal-DRI {dri_c:.1f} Mt DRI, NG-DRI {dri_n:.1f} Mt DRI, NG {dri_n*0.35:.2f} Mt")
print(f"scope1 {s1:.1f} Mt  scope2 {s2:.1f} Mt  total {s1+s2:.1f} Mt  intensity {(s1+s2)/D:.2f} t/tCS")
print(f"BF-BOF route s1 {(cc*2.79+pci*2.756+lime_bf*0.44)/bof:.2f} t/tCS ; coal-DRI route s1 {(dri_c*2.64+0.01*cd*2.64+0.06*cd*.44)/cd:.2f}")
print(f"power {pw/D:.0f} kWh/tCS gross, pellet share {200*(pel_bf+1.5*dri_c+1.5*dri_n)/pw:.0%}")
