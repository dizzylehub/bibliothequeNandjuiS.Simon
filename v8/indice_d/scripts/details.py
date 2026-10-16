"""Planches vectorielles de conception D — millimètres, à prototyper."""
from pathlib import Path
from html import escape
O=Path(__file__).resolve().parents[1]/'dessins'
INK='#2c302b';OLIVE='#646d52';WOOD='#c5a27d';PAPER='#fbfaf6'
class Sheet:
 def __init__(self,title,sub):
  self.e=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000"><rect width="1600" height="1000" fill="{PAPER}"/>'];self.text(65,65,title,32);self.text(65,103,sub,18,'#77776e');self.line(65,125,1535,125)
 def text(self,x,y,s,size=19,color=INK):self.e.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="Jost,Arial,sans-serif" font-size="{size}">{escape(s)}</text>')
 def line(self,x,y,u,v,w=1.5,color=INK,dash=''):self.e.append(f'<path d="M{x} {y} L{u} {v}" fill="none" stroke="{color}" stroke-width="{w}" stroke-dasharray="{dash}"/>')
 def rect(self,x,y,w,h,fill='none',r=0):self.e.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{INK}" stroke-width="1.5"/>')
 def path(self,d,fill='none',w=2):self.e.append(f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
 def dim(self,x,y,u,label):
  self.line(x,y,u,y,.8);self.line(x,y-9,x,y+9,.8);self.line(u,y-9,u,y+9,.8);self.text((x+u)/2-25,y-8,label,17)
 def note(self,x,y,num,text,tx,ty):
  self.e.append(f'<circle cx="{x}" cy="{y}" r="15" fill="{OLIVE}"/>');self.text(x-5,y+6,str(num),16,'white');self.text(x+26,y+6,text,18);self.line(x,y+20,tx,ty,.8,'#8e8d80')
 def save(self,name):
  self.text(65,960,'V8 · INDICE D  /  DÉTAILS DE CONCEPTION — dimensions proposées en mm ; assemblages et stabilité à valider au prototype.',16,'#77776e');self.e.append('</svg>');(O/name).write_text(''.join(self.e))

def armchair(terrace=False):
 s=Sheet('M05 / PALABRE' if terrace else 'M01 / PALME','Fauteuil de terrasse · bois durable, corde extérieure et coussins déhoussables' if terrace else 'Fauteuil de lecture · structure sculptée et assise souple')
 s.text(100,175,'ÉLÉVATION DE FACE',16,OLIVE);s.text(700,175,'PROFIL',16,OLIVE)
 # mm to 0.5px: 660mm wide, seat top 530mm, max height ~880mm
 for x in (160,440):s.path(f'M{x-13} 690 L{x+2} 475 L{x+25} 475 L{x+12} 690 Z',WOOD)
 s.rect(160,420,305,70,'#e5e5d6',26);s.rect(160,270,305,163,'#d1d6bf',30)
 s.path('M150 430 Q143 370 165 355 L175 355 L180 430',WOOD)
 s.path('M450 430 Q470 370 455 355 L445 355 L435 430',WOOD)
 s.dim(145,735,475,'670');s.line(110,250,110,690,.8);s.text(65,475,'≈900',16);s.line(95,250,125,250);s.line(95,690,125,690)
 s.path('M760 690 L785 470 L809 470 L784 690 Z',WOOD);s.path('M1060 690 L1005 470 L1026 465 L1084 690 Z',WOOD)
 s.rect(775,440,287,65,'#e5e5d6',25)
 s.path('M1010 442 L1046 263 Q1058 248 1077 260 L1083 281 L1042 465 Z','#d1d6bf')
 s.path('M775 391 Q853 350 970 366 Q1020 350 1063 311',w=17)
 s.line(780,460,790,390,9,WOOD);s.line(1013,490,1070,280,8,WOOD)
 s.dim(750,735,1090,'≈745' if terrace else '≈710');s.line(1130,425,1130,690,.8);s.text(1150,560,'assise 470',17)
 s.note(130,215,1,'Accoudoir galbé',170,358);s.note(735,215,2,'Dossier incliné de 12°',1055,290)
 s.text(100,815,'01  Tenon / mortaise à dimensionner ; arêtes au contact adoucies.',20)
 s.text(100,854,'02  Dessus d’assise proposé à 470 mm ; confort et compression à tester au prototype.',20)
 s.text(100,893,'03  Housse remplaçable ; mousse et support à ajuster pour le confort et l’usage.',20)
 s.save('M05_PALABRE.svg' if terrace else 'M01_PALME.svg')

def table():
 s=Sheet('M02 / GALET','Table d’hôtes · plateau capsule, deux socles oblongs et patins bronze')
 s.text(100,175,'PLAN',16,OLIVE);s.text(840,175,'ÉLÉVATION',16,OLIVE)
 s.rect(100,240,640,360,'#dbc4a8',180);s.rect(220,305,92,230,'none',46);s.rect(530,305,92,230,'none',46);s.dim(100,655,740,'1 600');s.text(25,430,'900',17)
 s.rect(855,340,640,16,WOOD,7)
 for x in (955,1305):s.rect(x,356,92,276,'#dbc4a8',10);s.rect(x-4,625,100,10,'#9d8556',4)
 s.dim(855,680,1495,'1 600');s.line(1520,340,1520,640,.8);s.text(1460,725,'H 750',17)
 s.note(900,220,1,'Plateau 40 mm / chant adouci R7',1050,340)
 s.text(100,810,'01  Fixation par inserts et trous oblongs pour accompagner les mouvements du bois.',21)
 s.text(100,852,'02  Vérifier le dégagement des genoux et la stabilité sous charge excentrée.',21)
 s.text(100,894,'03  Finition mate réparable ; protection contre les liquides et la chaleur.',21)
 s.save('M02_GALET.svg')

def chair():
 s=Sheet('M03 / LIANE','Chaise de table · dossier enveloppant, piètement fuselé, assise cognac')
 s.text(100,175,'FACE',16,OLIVE);s.text(800,175,'PROFIL',16,OLIVE)
 s.path('M170 320 Q300 240 440 320',w=30);s.rect(170,465,270,45,'#ad7956',22)
 for x in (190,420):s.path(f'M{x-10} 720 L{x+5} 510 L{x+23} 510 L{x+10} 720 Z',WOOD);s.line(x+10,480,x+10,320,10,WOOD)
 s.dim(160,765,450,'≈550');s.path('M850 720 L875 500 L895 500 L870 720 Z',WOOD);s.path('M1060 720 L1040 480 L1057 480 L1080 720 Z',WOOD)
 s.rect(860,465,220,45,'#ad7956',18);s.path('M1040 485 L1072 275',w=12);s.path('M1055 288 Q1085 272 1090 300',w=24)
 s.dim(850,765,1100,'≈570');s.note(780,220,1,'Dossier cintré / rayon à prototyper',1075,290)
 s.text(100,830,'Dessus d’assise proposé à 470 mm ; confort et stabilité à tester au prototype.',21)
 s.text(100,873,'Assemblages invisibles à éprouver ; patins de sol remplaçables ; garniture réparable.',21)
 s.save('M03_LIANE.svg')

def accueil():
 s=Sheet('M04 / RIVAGE','Comptoir d’accueil · façade arrondie, lattis fin et socle en retrait')
 s.text(100,175,'ÉLÉVATION',16,OLIVE);s.rect(100,250,720,20,WOOD,10);s.rect(116,270,688,376,'#e9dfd0',25)
 for x in range(240,690,20):s.rect(x,290,7,335,WOOD,3)
 s.rect(150,646,620,48,WOOD,10);s.dim(100,740,820,'1 800')
 s.text(960,175,'PLAN',16,OLIVE);s.rect(930,270,590,203,'#dbc4a8',101);s.dim(930,520,1520,'1 800');s.text(1320,565,'P 620 / H 1 055',18)
 s.text(100,822,'01  Prévoir un module bas accessible : hauteur et vide sous tablette à vérifier selon le programme.',20)
 s.text(100,863,'02  Trappe démontable, cheminement des câbles et ventilation des appareils à coordonner.',20)
 s.text(100,904,'03  Prototype de façade pour contrôler les joints, le rayon des retours et la résistance aux chocs.',20)
 s.save('M04_RIVAGE.svg')

def joints():
 s=Sheet('D01 / LE DÉTAIL FAIT LE MEUBLE','Principes d’assemblage · études graphiques, hors plans d’exécution')
 s.text(80,190,'01  BOIS / STRUCTURE',22,OLIVE);s.rect(130,290,145,320,WOOD);s.rect(275,345,210,100,WOOD);s.rect(220,370,90,50,'#e8d3b9');s.line(310,395,540,245);s.text(350,225,'Tenon + épaulement',18)
 s.text(640,190,'02  SELLERIE / ENTRETIEN',22,OLIVE);s.rect(650,320,310,125,'#d1d6bf',40);s.rect(650,445,310,30,WOOD,10);s.path('M665 357 Q800 345 945 357',w=2);s.line(880,350,1030,245);s.text(970,225,'Couture / passepoil',18)
 s.text(80,730,'03  TABLE / MOUVEMENT DU BOIS',22,OLIVE);s.rect(100,790,470,35,WOOD,9);s.rect(270,825,95,65,WOOD,8);s.rect(260,825,115,9,'#a99a70');s.path('M300 825 L300 800 M330 825 L330 800',w=3)
 s.text(700,670,'À mettre au point avec l’artisan',27)
 for i,t in enumerate(['Échantillon de finition à l’échelle 1.', 'Essai d’assise et de stabilité.', 'Jeux de dilatation et fixations démontables.', 'Accès aux housses et pièces d’usure.', 'Usage extérieur : drainage, UV et corrosion.']):s.text(700,720+i*35,t,20)
 s.save('D01_ASSEMBLAGES.svg')
armchair();armchair(True);table();chair();accueil();joints()
print('6 planches de détails écrites')
