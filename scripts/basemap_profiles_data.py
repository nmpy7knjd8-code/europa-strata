# Source of truth for data/kingdom-eras/basemap-profiles.json
P=[]
def add(id,names,name,type,years,summary,conflicts,leaders,religion,culture,story,sources,when=None):
    e=dict(id=id,names=names,name=name,type=type,yearsActive=years,summary=summary,description=summary,conflicts=conflicts,leaders=leaders,religion=religion,culture=culture,story=story,sources=sources)
    if when: e['when']=when
    P.append(e)
HM=lambda *ys:[f"high-medieval:{y}" for y in ys]
B="Encyclopaedia Britannica"
add("cyprus-medieval",["Cyprus"],"Cyprus","island realm","Byzantine to 1191; Lusignan kingdom 1192–1489",
 "A Byzantine province until the rebel Isaac Komnenos seized it in 1184. Richard I of England took the island in 1191 on his way to the Third Crusade and sold it; from 1192 the French Lusignan dynasty ruled a crusader Kingdom of Cyprus until Venice took over in 1489.",
 "Arab raids in earlier centuries; Richard I’s conquest (1191); Genoese seizure of Famagusta (1373); Mamluk invasion and the king’s capture (1426).",
 "Isaac Komnenos; Guy of Lusignan and Amalric, the first Lusignan rulers; Peter I, who led the sack of Alexandria in 1365.",
 "Greek Orthodox majority under a Latin Catholic church hierarchy imposed by the Lusignan kings.",
 "A Greek-speaking island ruled by a French-speaking court, with Italian merchant colonies in Famagusta.",
 "Lusignan Cyprus outlived the fall of Acre in 1291 and became the last Latin kingdom of the crusader East.",
 [B+", “Cyprus: History”","P. W. Edbury, The Kingdom of Cyprus and the Crusades, 1191–1374 (1991)"],
 when=HM(1000,1100,1200,1300,1400)+["renaissance:1400"])
add("sardinia-judicates",["Sardinia"],"Sardinia (the Judicates)","island judicates","c. 900s–1420",
 "After Byzantine control faded, Sardinia split into four self-governing realms called judicates (Cagliari, Arborea, Torres, Gallura), each ruled by a iudex. Pisa and Genoa competed for influence. Aragon claimed the island from 1297 and Arborea, the last judicate, gave in by 1420.",
 "Pisan–Genoese rivalry over the island; Aragon’s conquest from 1323; long Arborean resistance.",
 "Judges of Arborea, especially Eleanor of Arborea (d. c. 1404).",
 "Latin Christian, with Benedictine and other monasteries brought in from the mainland.",
 "Sardinian-language charters (condaghes) and the Carta de Logu law code of Arborea.",
 "Eleanor of Arborea’s Carta de Logu stayed in force on the island until 1827.",
 [B+", “Sardinia: History”"],when=HM(1000,1100,1200))
add("corsica-medieval",["Corsica"],"Corsica","island lordship","Pisan to 1284; Genoese 1284–1768",
 "Corsica was split among local lords under Pisan church overlordship until Genoa defeated Pisa at Meloria in 1284. Genoa then ruled the island, sometimes through the Bank of Saint George, until it was sold to France in 1768.",
 "Pisa–Genoa wars; Aragonese claims; revolts by local lords against Genoa.",
 "Archbishops of Pisa held church authority; later Genoese governors and the Bank of Saint George.",
 "Latin Christian, with Pisan Romanesque churches across the island.",
 "Mountain clan society with a Tuscan-influenced Corsican language.",
 "The Pisan Romanesque churches built across the island in the 1100s still stand.",
 [B+", “Corsica: History”"],when=HM(1000,1100,1200,1300,1400))
add("georgia-medieval",["Georgia","Kingdom of Georgia"],"Kingdom of Georgia","kingdom","1008–1490s (unified kingdom)",
 "Bagrat III united the Georgian lands as one kingdom in 1008. David IV the Builder drove out the Seljuks, winning at Didgori in 1121 and taking Tbilisi in 1122, and the kingdom reached its height under Queen Tamar (1184–1213). Mongol rule from the 1230s and Timur’s invasions wore it down, and by the 1490s it had split into rival kingdoms and principalities.",
 "Seljuk wars; Didgori (1121); Khwarezmian and Mongol invasions (1220s–1240s); Timur’s campaigns (1386–1403).",
 "Bagrat III; David IV the Builder; Queen Tamar; George V the Brilliant, who restored the kingdom after the Mongols.",
 "Georgian Orthodox Christianity, with monasteries such as Gelati at the centre of learning.",
 "A golden age of Georgian literature and church building.",
 "Shota Rustaveli’s epic The Knight in the Panther’s Skin dates from Tamar’s reign.",
 [B+", “Georgia: History”","R. G. Suny, The Making of the Georgian Nation (1994)"],
 when=HM(1000,1100,1200,1300,1400)+["renaissance:1400","renaissance:1500"])
add("armenia-medieval",["Armenia"],"Armenia","kingdom, then lordships","Bagratid kingdom 885–1045; then Byzantine, Seljuk and Georgian overlords",
 "Around 1000 the Bagratid kings ruled from Ani, a city of churches on the Silk Road. Byzantium annexed Ani in 1045 and the Seljuks sacked it in 1064. In the 1100s and 1200s Armenian lords such as the Zakarids governed much of the region under Georgian protection.",
 "Byzantine annexation (1045); Seljuk conquest after Manzikert (1071); Mongol invasions from the 1230s.",
 "Gagik I of Ani; the Zakarid brothers Zakare and Ivane.",
 "Armenian Apostolic Church, with monastic centres such as Haghpat and Sanahin.",
 "Armenian stone churches, carved khachkar cross-stones and manuscript illumination.",
 "Ani became known as the ‘city of 1001 churches’.",
 [B+", “Armenia: History”","R. G. Hovannisian (ed.), The Armenian People from Ancient to Modern Times, vol. 1 (1997)"],
 when=HM(1000,1100,1200))
add("buyids",["Buwayhid Emirates"],"Buyid (Buwayhid) emirates","dynastic emirates","934–1062",
 "The Buyids were a Shi‘i dynasty from Daylam that took Baghdad in 945 and ruled Iraq and western Iran in the caliph’s name. The Seljuk Turks ended their rule between 1055 and 1062. The basemap uses the label loosely for the upper Mesopotamian borderlands, where Kurdish and Arab dynasties also ruled.",
 "Rivalry with the Hamdanids, Byzantium and the Ghaznavids; Seljuk conquest of Baghdad (1055).",
 "Adud al-Dawla (d. 983), the strongest Buyid ruler.",
 "Twelver Shi‘i rulers who governed under the Sunni Abbasid caliph.",
 "Persian court culture in Arabic and Persian; patronage of scholars and hospitals in Baghdad.",
 "Adud al-Dawla’s hospital in Baghdad was founded in the 980s.",
 [B+", “Buyid dynasty”"],when=HM(1000,1200))
add("benevento",["Duchy of Benevento"],"Principality of Benevento","Lombard principality","571–1077 (principality from 774)",
 "Benevento was the longest-lived Lombard state in southern Italy. It survived Charlemagne’s conquest of the Lombard kingdom in 774 as an independent principality. By 1000 it had lost Salerno and Capua as separate states. In the 1000s the city passed to the papacy and the Normans took over its lands.",
 "Wars with Byzantium, Arab raiders and Carolingian kings; Norman expansion in the 1000s.",
 "Arechis II, who took the title of prince in 774.",
 "Latin Christian, with the abbeys of Monte Cassino and San Vincenzo al Volturno nearby.",
 "Lombard law and Beneventan script, a distinctive southern Italian handwriting.",
 "The Beneventan script used by its monks gives the region its name in manuscript studies.",
 [B+", “Benevento”"],when=HM(1000))
add("aragon-1000",["Aragón"],"County of Aragon","county","c. 800s–1035 (then kingdom)",
 "Aragon began as a small Pyrenean county around Jaca. In 1000 it was tied to the Kingdom of Pamplona (Navarre). After Sancho III of Navarre died in 1035, his son Ramiro I ruled Aragon on his own, and it later grew into the Crown of Aragon.",
 "Frontier warfare with the Muslim taifas of the Ebro valley.",
 "Sancho III of Navarre; Ramiro I, the first king of Aragon (from 1035).",
 "Latin Christian, with mountain monasteries such as San Juan de la Peña.",
 "A Pyrenean frontier society that spoke an early form of Aragonese.",
 "From this small county came the Crown of Aragon, later a Mediterranean power.",
 [B+", “Aragon”"],when=HM(1000))
add("brittany",["Britany"],"Duchy of Brittany","duchy","939–1532 (union with France)",
 "Brittany was a Breton-speaking duchy in the far west of France. It recognised the French king as overlord but governed itself. In the 1300s the War of the Breton Succession ended with the Montfort dukes in power. Anne of Brittany’s marriages to two French kings led to Brittany’s union with France in 1532.",
 "Norman and Angevin pressure; War of the Breton Succession (1341–1364); French invasion (1487–1491).",
 "Alan IV; John IV and John V of Montfort; Duchess Anne (1488–1514).",
 "Latin Christian, with strong cults of local saints.",
 "Breton language in the west and Gallo in the east, with a ducal court at Nantes.",
 "Anne of Brittany married Charles VIII and then Louis XII of France.",
 [B+", “Brittany”"],when=HM(1000,1100)+["renaissance:1400"])
add("sami",["Samis","Sámi"],"Sámi lands (Sápmi)","indigenous homeland","prehistoric–present",
 "The Sámi are the indigenous people of northern Scandinavia, Finland and the Kola Peninsula. They had no state of their own and lived in local communities called siida, based on hunting, fishing and, later, reindeer herding. Norwegian, Swedish and Russian rulers competed to tax them from the Middle Ages on.",
 "Overlapping tax claims by Norway, Sweden and Novgorod (later Russia).",
 "No kings; leadership came from siida elders and noaidi (shamans).",
 "Traditional Sámi religion, with Christian missions growing from the 1600s.",
 "Sámi languages, joik song and a herding and fishing economy.",
 "Norse and Russian sources describe the Sámi as fur traders and skiers.",
 [B+", “Sami”","N. Kent, The Sámi Peoples of the North (2014)"])
add("finnic-forest",["Finno-Ugric taiga hunter-gatherers","Paleo-Siberian hunter-gatherers","Siberians"],"Northern forest peoples","peoples, not states","—",
 "The basemap uses this label for the forest and tundra peoples of the far northeast. They include Finno-Ugric and Samoyedic groups who lived by hunting, fishing and the fur trade. They had no state. Novgorod traders, and later Moscow, gradually brought them into a tribute system.",
 "Tribute collection by Novgorod and later Moscow, especially for furs.",
 "No state rulers; kin and clan leaders.",
 "Animist and shamanic religion.",
 "Hunting, reindeer herding and the fur trade.",
 "Novgorod’s ‘Yugra’ fur expeditions reached the Urals in the 1000s and 1100s.",
 [B+", “Finno-Ugric peoples”",B+", “Samoyed”"])
add("karelians",["Karelians"],"Karelians","Finnic people","—",
 "The Karelians are a Finnic people of the lands between the Gulf of Finland, Lake Ladoga and the White Sea. Around 1000 they traded furs with Novgorod. Sweden and Novgorod later fought over Karelia and divided it in the Treaty of Nöteborg (1323).",
 "Swedish–Novgorodian wars over Karelia.",
 "No kings; local chiefs.",
 "Pagan religion, gradually replaced by Orthodox Christianity under Novgorod’s influence.",
 "Karelian oral poetry, later collected in the Kalevala.",
 "Birch-bark letters found in Novgorod include a short text in a Finnic language.",
 [B+", “Karelia”"],when=HM(1000))
add("suomi",["Suomi"],"Finns (Suomi)","Finnic people","—",
 "This label covers the Finns of southwest Finland around 1000. They lived in farming and trading communities with no central state. Swedish crusades and Catholic missions brought the region under Sweden from the 1100s and 1200s.",
 "Swedish crusades into Finland; Novgorodian raids.",
 "No kings; local communities.",
 "Pagan religion, followed by Catholic conversion under Sweden.",
 "Iron Age farming and hill forts.",
 "‘Suomi’ is still the Finnish name for Finland.",
 [B+", “Finland: History”"],when=HM(1000))
add("chuds",["Chuds"],"Chuds","Finnic peoples","—",
 "‘Chud’ is the old Russian name for the Finnic peoples east of the Baltic, especially the ancestors of the Estonians and Votes. The Russian Primary Chronicle lists them among the peoples who invited the Varangians to rule.",
 "Raids and campaigns by Kiev and Novgorod; later the Livonian crusade.",
 "No kings; local elders.",
 "Pagan religion.",
 "Hill forts and farming villages.",
 "The battle on the ice of Lake Peipus (1242) was fought on Lake Chud, as Russians call it.",
 [B+", “Chud”"],when=HM(1000))
add("curonians",["Kurs"],"Curonians (Kurs)","Baltic people","—",
 "The Curonians were a Baltic people of the coast of modern Latvia and Lithuania, known as seafarers and raiders. German crusaders conquered them in the 1200s, and Courland is named after them.",
 "Raids on Scandinavia; the Livonian crusade.",
 "No kings; local chiefs.",
 "Baltic pagan religion.",
 "Seafaring, hill forts and amber trade.",
 "Danish and Swedish chronicles describe Curonian raids across the Baltic.",
 [B+", “Courland”"],when=HM(1000))
add("kimek-kipchak",["Kimek-Kipchak khaganate"],"Kimek–Kipchak confederation","nomad confederation","c. 800s–1000s",
 "The Kimek–Kipchak confederation was a union of Turkic tribes on the Irtysh and the steppe east of the Volga. By the early 1000s the Kipchak tribes had pushed west and taken over the Pontic steppe, where Rus called them Polovtsy and Byzantines called them Cumans.",
 "Wars with the Oghuz and Pechenegs; later raids on Rus.",
 "Tribal khans.",
 "Tengrist religion, with some Islamic and Manichaean influence.",
 "Horse-herding nomads on the steppe.",
 "The Kipchak language became the basis of the later Golden Horde’s Turkic.",
 [B+", “Kipchak”"],when=HM(1000))
add("volga-bulgaria",["Volga Bulgars"],"Volga Bulgaria","khanate","c. 900s–1236",
 "Volga Bulgaria was a Turkic state at the meeting point of the Volga and Kama. It adopted Islam in 922, when ibn Fadlan arrived as the caliph’s envoy. It grew rich on the fur trade from its capital Bolghar, until the Mongols destroyed it in 1236.",
 "Wars with the Rus principalities; Mongol conquest (1236).",
 "Almış, the ruler who received the caliph’s mission.",
 "Sunni Islam since 922.",
 "Trade in furs, slaves and silver between the northern forests and the Islamic world.",
 "Ibn Fadlan’s report on his journey also describes the Rus traders he met.",
 [B+", “Bulgar (people)”"],when=HM(1000,1100,1200))
add("arran",["Arran"],"Arran","region and emirates","—",
 "Arran is the medieval name for the land between the Kura and Araxes rivers, now in Azerbaijan. Around 1000–1100 the Kurdish Shaddadid dynasty ruled much of it from Ganja, until the Seljuks took control.",
 "Wars with Georgia, Shirvan and the Seljuks.",
 "Shaddadid emirs of Ganja.",
 "Islam, with Christian Albanian and Armenian communities.",
 "Persian-speaking town culture.",
 "The poet Nizami Ganjavi (d. c. 1209) was born in Ganja.",
 [B+", “Ganja”","V. Minorsky, Studies in Caucasian History (1953)"],when=HM(1000,1100))
add("shirvan",["Shirvan"],"Shirvan (the Shirvanshahs)","Muslim principality","c. 861–1538",
 "Shirvan was a principality on the Caspian coast of modern Azerbaijan, ruled by the Shirvanshahs from Shamakhi and later Baku. It survived for centuries as a client of larger powers until the Safavids annexed it in 1538.",
 "Raids from the steppe; Georgian, Seljuk and Mongol overlordship; Safavid conquest (1538).",
 "Shirvanshahs of the Yazidid and Kasranid dynasties.",
 "Islam.",
 "Persian court culture and poetry.",
 "The Palace of the Shirvanshahs in Baku dates from the 1400s.",
 [B+", “Shirvan”"],when=HM(1000,1100))
add("alania",["Alans"],"Alania","kingdom","c. 900s–1239",
 "Alania was a Christian kingdom of the Alans, an Iranian-speaking people of the North Caucasus. It was allied with Byzantium and Georgia, and the Mongols destroyed it in 1238–1239. The Ossetians are their descendants.",
 "Wars with the Khazars; Mongol invasion (1238–1239).",
 "Alan kings who married into the Georgian royal family.",
 "Orthodox Christianity, adopted under Byzantine missions in the 900s.",
 "Iranian-speaking mountain and steppe culture.",
 "Church ruins in the upper Kuban valley mark the old Alan capital.",
 [B+", “Alani”"],when=HM(1000,1100))
add("khazars",["Khazars"],"Khazar Khaganate (remnant)","khaganate","c. 650–969",
 "The Khazars were a Turkic khaganate between the Volga, Don and Caucasus. They controlled steppe trade for three centuries, and their elite adopted Judaism. Sviatoslav of Kiev broke their power in 965–969, and by 1000 only a weak remnant was left.",
 "Arab–Khazar wars; Sviatoslav’s campaigns (965–969).",
 "The khagan and the bek, who held the real power.",
 "A Jewish ruling elite, with Muslim, Christian and pagan subjects.",
 "A trading state that charged tolls on the Volga trade.",
 "Their capital Atil, on the Volga delta, has never been firmly located.",
 [B+", “Khazar”","P. B. Golden et al. (eds.), The World of the Khazars (2007)"],when=HM(1000))
add("serbia-medieval",["Serbia"],"Serbian principalities","principalities","c. 800s–1100s",
 "Around 1000–1100 the Serbs were split between Raška in the interior and Duklja on the coast, mostly under Byzantine overlordship. Stefan Nemanja (r. 1166–1196) later united them and founded the Nemanjić state.",
 "Revolts against Byzantium; wars with Hungary.",
 "Vukan of Raška; Constantine Bodin of Duklja.",
 "Christianity, between Rome and Constantinople until the Serbian Orthodox Church became self-governing in 1219.",
 "Slavic hill-country society.",
 "Duklja’s rulers received a royal crown from the pope in 1077.",
 [B+", “Serbia: History”"],when=HM(1000,1100))
add("pechenegs",["Peshemegs"],"Pechenegs","nomad confederation","c. 800s–1091",
 "The Pechenegs were Turkic nomads who held the Pontic steppe from the 800s. Byzantium paid them to fight its enemies, and they also fought Kiev. Byzantium and the Cumans crushed them at Levounion in 1091.",
 "Siege of Kiev (968); raids into Byzantium; Levounion (1091).",
 "Tribal khans.",
 "Tengrist religion, with some conversions to Islam and Christianity.",
 "Mounted nomads.",
 "The Byzantine emperor Constantine VII described their eight tribes in the 900s.",
 [B+", “Pecheneg”"],when=HM(1000))
add("croatia-1100",["Croatia"],"Kingdom of Croatia","kingdom","925–1102 (then in union with Hungary)",
 "Medieval Croatia became a kingdom under Tomislav around 925. After its native dynasty died out, the Croatian nobles accepted Coloman of Hungary as king in 1102. Croatia kept its own institutions inside the union.",
 "The succession war after 1091; Venetian rivalry on the Dalmatian coast.",
 "Tomislav; Peter Krešimir IV; Demetrius Zvonimir; Coloman of Hungary.",
 "Catholic Christianity, with Glagolitic liturgy on the coast.",
 "A Dalmatian town and Slavic hinterland.",
 "The Baška tablet (c. 1100) is one of the oldest Croatian inscriptions.",
 [B+", “Croatia: History”"],when=HM(1100))
add("bulgaria-medieval",["Bulgar Khanate"],"Bulgaria","Byzantine province, then empire","First Empire to 1018; Byzantine 1018–1185; Second Empire 1185–1396",
 "In the Balkans the basemap uses this label for the Bulgarian lands. Byzantium conquered the First Bulgarian Empire in 1018. The Asen brothers founded the Second Bulgarian Empire in 1185, ruling from Tarnovo. The Ottomans conquered it between 1393 and 1396, so by 1400 the label is out of date.",
 "Basil II’s war (1014–1018); the Asen revolt (1185); Ottoman conquest (1393–1396).",
 "Peter and Ivan Asen; Kaloyan; Ivan Asen II; Ivan Shishman.",
 "Bulgarian Orthodox Church.",
 "Old Church Slavonic literature and the Tarnovo school of writers.",
 "Ivan Asen II’s Tarnovo was a centre of Slavic Orthodox learning.",
 [B+", “Bulgaria: History”"],when=HM(1100,1400)+["renaissance:1400"])
add("karakalpaks-1100",["Karakalpaks"],"Black Hats (Karakalpaks)","nomad groups","—",
 "‘Karakalpak’ means ‘black hat’ in Turkic. Rus chronicles call the Turkic nomads who settled as border guards for Kiev the Chorni Klobuky, or ‘black hoods’. The basemap places the label schematically.",
 "Border service for Kiev against the Cumans.",
 "Tribal chiefs.",
 "Mostly Tengrist religion.",
 "Mounted nomad auxiliaries.",
 "They are distinct from the modern Karakalpaks of Uzbekistan, who share the name.",
 [B+", “Chorni Klobuky”"],when=HM(1100))
CAU=[
 ("maskut",["Maskat"],"Maskut","small principality","A small principality on the Caspian coast north of Derbent, known from Arab and Armenian sources."),
 ("derbent",["Derbent"],"Emirate of Derbent","emirate","An Arab-led emirate based at the fortress city of Derbent, the Caspian ‘gate’ between the steppe and the Middle East. The Hashimid dynasty ruled it until the Seljuk era."),
 ("sarir",["Khundzi"],"Sarir (Khunzakh)","mountain kingdom","The Christian Avar kingdom of Sarir in highland Dagestan, centred on Khunzakh. It later converted to Islam."),
 ("tashir",["Tashir"],"Kingdom of Tashir-Dzoraget","Armenian kingdom","A Bagratid Armenian kingdom in the Lori region, founded in the 980s. In the 1100s it became a vassal of Georgia."),
 ("khachen",["Artsakh"],"Principality of Khachen (Artsakh)","Armenian principality","An Armenian princely state in the mountains of Artsakh (Karabakh). Local princes kept it going under Seljuk, Georgian and Mongol overlords."),
 ("durdzuks",["Durdzuks"],"Durdzuks","highland people","The Georgian name for the Vainakh highlanders, ancestors of the Chechens and Ingush. They lived in clan communities with no state."),
 ("lakz",["Leks"],"Lakz","highland principality","A highland principality in southern Dagestan, linked to the Lezgins, mentioned by Arab geographers."),
 ("kakheti-hereti",["Kakheti-Hereti"],"Kingdom of Kakheti-Hereti","kingdom","An eastern Georgian kingdom that David IV the Builder annexed into united Georgia in 1104."),
 ("tiflis-emirate",["Emirate of Tiflis"],"Emirate of Tiflis","emirate","An Arab-ruled city-state at Tbilisi that lasted from the 700s until David IV took the city in 1122 and made it Georgia’s capital."),
 ("goghtn",["Goghtn"],"Goghtn","Armenian district","A district on the Araxes near Nakhchivan, historically an Armenian province, under Seljuk and local rulers in this period."),
 ("syunik",["Syunik"],"Kingdom of Syunik","Armenian kingdom","An Armenian kingdom in the southern highlands (also called Baghk). The Seljuks took its last fortresses in 1170."),
]
for id,names,name,typ,summ in CAU:
    add(id,names,name,typ,"c. 900s–1100s",summ+" It was one of many small states in the Caucasus between Byzantium, Georgia and the Seljuks.",
        "Wars among neighbouring Caucasian states; Seljuk invasions from the 1060s.",
        "Local princely and emiral dynasties.",
        "Christian or Muslim, depending on the ruling house.",
        "Mountain and valley communities speaking Caucasian languages, Armenian, Georgian, Arabic or Persian.",
        "These small states show how fragmented the Caucasus was before David IV’s Georgia and the Mongols.",
        [B+", “Caucasus: History”","V. Minorsky, A History of Sharvan and Darband (1958)"],when=HM(1100))
add("rus-principalities",["Other Rus Principalities"],"Other Rus principalities","principalities","c. 1130s–1240s",
 "After 1132 Kievan Rus split into separate principalities ruled by branches of the Rurikid dynasty, including Chernigov, Smolensk, Polotsk and Turov-Pinsk. They shared the Orthodox faith and the Rurikid dynasty. Most fell under Mongol overlordship from 1237–1240.",
 "Princely feuds over Kiev; Cuman raids; Mongol invasion (1237–1240).",
 "Rurikid princes of each principality.",
 "Orthodox Christianity under the metropolitan of Kiev.",
 "Old East Slavic chronicles and church building.",
 "The Tale of Igor’s Campaign describes a Novgorod-Seversky prince’s raid of 1185.",
 [B+", “Kievan Rus”"],when=HM(1200))
add("toulouse",["Comté de Toulouse"],"County of Toulouse","county","c. 778–1271",
 "Toulouse was a large southern French county and a centre of Occitan court culture. Around 1200 the Cathar heresy spread under Count Raymond VI. The Albigensian Crusade from 1209 broke the county, and it passed to the French crown in 1271.",
 "Albigensian Crusade (1209–1229); Muret (1213); Treaty of Paris (1229).",
 "Raymond VI and Raymond VII.",
 "Catholic, with widespread Catharism.",
 "Occitan troubadour poetry.",
 "Simon de Montfort was killed besieging Toulouse in 1218.",
 [B+", “Albigenses”",B+", “Toulouse”"],when=HM(1200))
add("ryazan",["Ryazan"],"Grand Principality of Ryazan","principality","1129–1521",
 "Ryazan was a Rus principality on the Oka. The Mongols sacked it first, in December 1237. It survived as a buffer between Moscow and the steppe until Moscow annexed it in 1521.",
 "Mongol sack (1237); rivalry with Moscow.",
 "Oleg Ivanovich (r. 1350–1402), who manoeuvred between Moscow and the Horde.",
 "Orthodox Christianity.",
 "A frontier principality on the forest-steppe edge.",
 "The tale of Evpaty Kolovrat tells of Ryazan’s resistance to Batu.",
 [B+", “Ryazan”"],when=HM(1300))
add("mamluks",["Mamluke Sultanate"],"Mamluk Sultanate","sultanate","1250–1517",
 "The Mamluk Sultanate ruled Egypt and Syria from Cairo. Its rulers were slave-soldiers who seized power in 1250. They stopped the Mongols at Ain Jalut in 1260 and took the last crusader cities by 1291. The Ottomans conquered it in 1516–1517.",
 "Ain Jalut (1260); fall of Acre (1291); Timur’s invasion of Syria (1400–1401); Ottoman conquest (1516–1517).",
 "Baybars; Qalawun; al-Nasir Muhammad; Qaitbay.",
 "Sunni Islam; the sultans hosted a shadow Abbasid caliphate in Cairo.",
 "Cairo’s madrasas, mosques and scholarship.",
 "Historians such as Ibn Khaldun and al-Maqrizi worked in Mamluk Cairo.",
 [B+", “Mamluk”"],when=HM(1300,1400)+["renaissance:1400","renaissance:1500"])
add("trebizond",["Trebizond"],"Empire of Trebizond","Byzantine successor state","1204–1461",
 "The Empire of Trebizond was a Greek state on the Black Sea coast of Anatolia, founded by Komnenos princes as the Fourth Crusade took Constantinople. It lived on trade and diplomatic marriages until Mehmed II took it in 1461.",
 "Seljuk and Turkmen pressure; Ottoman conquest (1461).",
 "Alexios I; Alexios III; David, the last emperor.",
 "Greek Orthodox Christianity.",
 "Byzantine court culture on a Silk Road port.",
 "Trebizond outlasted Constantinople by eight years.",
 [B+", “Trebizond, Empire of”"],when=HM(1300,1400)+["renaissance:1400"])
add("rum-seljuks",["Seljuk Caliphate"],"Seljuk Sultanate of Rum and successor beyliks","sultanate, then beyliks","1077–1308",
 "The Seljuks of Rum ruled central Anatolia from Konya. After their defeat at Köse Dağ in 1243 they were vassals of the Mongol Ilkhanate, and the sultanate ended around 1308. On the 1400 map the label stands for the Turkish beyliks that followed, such as Karaman.",
 "Manzikert (1071); Myriokephalon (1176); Köse Dağ (1243).",
 "Kilij Arslan II; Kayqubad I.",
 "Sunni Islam, with Sufi orders and Christian subjects.",
 "Persian court culture, caravanserais and Konya’s mosques.",
 "Rumi, the Sufi poet, lived and taught in Seljuk Konya.",
 [B+", “Rum, Sultanate of”"],when=HM(1300,1400)+["renaissance:1400"])
add("ilkhanate",["Ilkhanate"],"Ilkhanate","Mongol khanate","1256–1335",
 "The Ilkhanate was a Mongol state founded by Hülegü, who sacked Baghdad in 1258. It ruled Iran, Iraq and eastern Anatolia from Tabriz. Ghazan converted to Islam in 1295. The state broke up after Abu Sa‘id died in 1335.",
 "Sack of Baghdad (1258); wars with the Mamluks and the Golden Horde.",
 "Hülegü; Ghazan; Öljeitü.",
 "Shamanist and Buddhist rulers at first, then Islam from 1295.",
 "Persian historiography and miniature painting.",
 "Rashid al-Din’s world history was written for the Ilkhans.",
 [B+", “Il-Khanid dynasty”"],when=HM(1300))
add("aydin",["Beylik of Aydin"],"Beylik of Aydın","Turkish beylik","c. 1308–1426",
 "Aydın was a Turkish emirate on the Aegean coast around Smyrna and Ephesus (Ayasoluk), known for its fleets. The Ottomans annexed it, finally in 1426.",
 "Naval raids in the Aegean; the crusade that took Smyrna (1344).",
 "Umur Bey.",
 "Sunni Islam.",
 "Coastal Turkish frontier culture.",
 "The İsa Bey Mosque at Selçuk was built in 1375.",
 [B+", “Aydın”"],when=HM(1400)+["renaissance:1400"])
add("moldavia-1400",["Moldova"],"Principality of Moldavia","principality","c. 1359–1859",
 "Moldavia was founded around 1359 east of the Carpathians when Bogdan I broke away from Hungary. Under Alexander the Good (1400–1432) it controlled trade between the Black Sea and Poland.",
 "Pressure from Hungary and Poland; later Ottoman wars.",
 "Bogdan I; Alexander the Good; later Stephen the Great.",
 "Orthodox Christianity.",
 "Romanian-speaking boyar society, with Church Slavonic as the written language.",
 "Alexander the Good strengthened the port of Cetatea Albă (Akkerman).",
 [B+", “Moldavia”"],when=HM(1400))
add("timurids",["Timurid Empire"],"Timurid Empire","empire","1370–1507",
 "Timur conquered an empire from Central Asia to Anatolia and ruled from Samarkand. He defeated the Ottomans at Ankara in 1402. His successors ruled a smaller state from Herat and Samarkand until about 1507.",
 "Ankara (1402); sacks of Delhi, Baghdad and Damascus.",
 "Timur; Shah Rukh; Ulugh Beg.",
 "Sunni Islam.",
 "Persianate court art and architecture.",
 "Ulugh Beg’s observatory at Samarkand was built in the 1420s.",
 [B+", “Timurid dynasty”"],when=HM(1400)+["renaissance:1400"])
add("bosnia-1400",["Bosnia"],"Kingdom of Bosnia","kingdom","1377–1463",
 "Tvrtko I made Bosnia a kingdom in 1377. Its silver mines made it rich. The Ottomans conquered it in 1463.",
 "Hungarian intervention; Ottoman conquest (1463).",
 "Tvrtko I; Stephen Tomašević, the last king.",
 "Catholic, Orthodox and the independent Bosnian Church.",
 "Carved stećci tombstones.",
 "Thousands of stećci still stand across Bosnia.",
 [B+", “Bosnia and Herzegovina: History”"],when=["renaissance:1400"])
add("aq-qoyunlu",["Emirate of the White Sheep Turks"],"Aq Qoyunlu (White Sheep Turkmen)","Turkmen confederation","1378–1503",
 "The Aq Qoyunlu was a Turkmen confederation that ruled eastern Anatolia, Iraq and Iran from Diyarbakır and later Tabriz. Ismail I’s Safavids replaced it in the early 1500s.",
 "Wars with the Kara Koyunlu, the Ottomans (Otlukbeli, 1473) and the Safavids.",
 "Uzun Hasan.",
 "Sunni Islam.",
 "Persianate court culture at Tabriz.",
 "Uzun Hasan exchanged envoys with Venice against the Ottomans.",
 [B+", “Ak Koyunlu”"],when=["renaissance:1500"])
add("golden-horde",["Golden Horde"],"Golden Horde","Mongol khanate","1240s–1502",
 "The Golden Horde, or Ulus of Jochi, was the Mongol khanate of the western steppe, ruled from Sarai on the Volga. It took tribute from the Rus principalities. It split into separate khanates in the 1400s and its last remnant fell to the Crimean Khanate in 1502.",
 "Kulikovo (1380); Timur’s campaigns (1390s); the Great Stand on the Ugra (1480).",
 "Batu; Özbeg; Tokhtamysh.",
 "Islam from Özbeg’s reign (1313–1341).",
 "Kipchak Turkic steppe culture.",
 "Moscow stopped paying it tribute after 1480.",
 [B+", “Golden Horde”"],when=["renaissance:1500"])
add("white-horde",["White Horde"],"White Horde","Mongol khanate","c. 1220s–1400s",
 "‘White Horde’ is the name for the eastern wing of Jochi’s ulus, on the steppe of modern Kazakhstan. Historians use the term inconsistently. Its lands later became the base of the Uzbek and Kazakh khanates.",
 "Wars over the succession to the Golden Horde.",
 "Descendants of Jochi.",
 "Tengrism, gradually replaced by Islam.",
 "Steppe nomads.",
 "Tokhtamysh came from this wing before he took Sarai.",
 [B+", “Golden Horde”"],when=["renaissance:1500"])
add("astrakhan",["Astrakhan Khanate"],"Khanate of Astrakhan","khanate","c. 1466–1556",
 "Astrakhan was a Tatar successor of the Golden Horde on the lower Volga. Ivan IV annexed it in 1556, which gave Muscovy the whole Volga.",
 "Wars with Crimea and the Nogais; Russian conquest (1556).",
 "Its own line of Jochid khans.",
 "Sunni Islam.",
 "A river-mouth trading town.",
 "Its fall opened the Caspian trade to Russia.",
 [B+", “Astrakhan”"],when=["renaissance:1550"])
add("kazan",["Kazan Khanate"],"Khanate of Kazan","khanate","1438–1552",
 "Kazan was a Tatar khanate on the middle Volga, a successor of the Golden Horde. Ivan IV stormed Kazan in 1552.",
 "Repeated wars with Muscovy; siege of Kazan (1552).",
 "Ulugh Muhammad, the founder.",
 "Sunni Islam.",
 "Volga Tatar towns and trade.",
 "St Basil’s Cathedral in Moscow celebrates Ivan IV’s capture of Kazan.",
 [B+", “Kazan, khanate of”"],when=["renaissance:1550"])
add("nogai",["Nogai Horde"],"Nogai Horde","nomad horde","late 1300s–1630s",
 "The Nogai Horde was a confederation of Turkic nomads between the Volga and the Ural River, named after the Golden Horde general Nogai. Around 1600 it broke up under pressure from Russia and the Kalmyks.",
 "Raids on Muscovy; Kalmyk invasion (1630s).",
 "Beys descended from Edigu.",
 "Sunni Islam.",
 "Nomadic horse breeders who supplied horses to Moscow.",
 "Nogai horse herds were driven to Moscow to sell by the tens of thousands.",
 [B+", “Nogay”"])
add("kazakh-khanate",["Quazaq Khanate"],"Kazakh Khanate","khanate","1465–1847",
 "The Kazakh Khanate was founded around 1465 by Janibek and Kerei. It ruled the steppe east of the Ural River and later split into three hordes, or juz. From the 1700s they gradually came under Russian rule.",
 "Wars with the Uzbeks and the Dzungars.",
 "Janibek; Kerei; Kasym Khan.",
 "Sunni Islam alongside steppe customs.",
 "Nomadic pastoralism and oral epic.",
 "Kazakh historians date their statehood from 1465.",
 [B+", “Kazakhstan: History”"])
add("finnmark",["Finnmark"],"Finnmark","Danish–Norwegian county","—",
 "Finnmark was Norway’s Arctic frontier, ruled for Denmark–Norway from the fortress of Vardøhus. Norwegian fishermen and Sámi lived there, and Sweden and Russia also claimed to tax the area.",
 "Kalmar War (1611–1613) over northern claims.",
 "Governors of Vardøhus.",
 "Lutheran Christianity; Sámi religion persisted.",
 "Cod fishing and reindeer herding.",
 "Vardø was the scene of witch trials in the 1600s.",
 [B+", “Finnmark”"])
add("pontremoli",["Pontremoli"],"Pontremoli","Tuscan territory","Tuscan from 1650",
 "Pontremoli is a town in the Lunigiana valley. Spanish Milan sold it to Genoa in 1647, and the Grand Duchy of Tuscany bought it in 1650. It stayed a Tuscan exclave until the 1840s.",
 "Its value as an Apennine pass was contested.",
 "Medici and Lorraine grand dukes of Tuscany.",
 "Catholic.",
 "A small market town on the Via Francigena.",
 "Its castle, the Piagnaro, guards the pass.",
 [B+", “Pontremoli”"])
add("fivizzano",["Fivizzano"],"Fivizzano","Tuscan territory","Florentine from 1477",
 "Fivizzano was a Florentine, and later Tuscan, enclave in Lunigiana. It passed to Modena in the 1840s.",
 "Border disputes among Tuscany, Modena and Genoa.",
 "Grand dukes of Tuscany.",
 "Catholic.",
 "A hill town.",
 "Jacopo da Fivizzano’s early printing press worked here in the 1470s.",
 [B+", “Lunigiana”"])
add("modena",["Modena"],"Duchy of Modena and Reggio","duchy","1452–1859",
 "The Este family ruled Modena and Reggio. After losing Ferrara to the pope in 1598 they made Modena their capital. From 1814 a Habsburg-Este line ruled until 1859, when the duchy joined united Italy.",
 "Wars of the Spanish and Austrian Successions; the 1831 uprising; 1859.",
 "Cesare d’Este; Francis IV.",
 "Catholic.",
 "The Este court library and art collection.",
 "The Biblioteca Estense keeps the Este Bible.",
 [B+", “Modena”"])
add("parma",["Parma"],"Duchy of Parma and Piacenza","duchy","1545–1859",
 "Parma and Piacenza were created as a duchy for the Farnese family in 1545. Spanish Bourbons followed in 1748. Napoleon’s widow Marie Louise ruled from 1814 to 1847. The duchy joined Italy in 1860.",
 "Successions after the Farnese line ended in 1731.",
 "Alessandro Farnese; Marie Louise.",
 "Catholic.",
 "The Teatro Farnese and Correggio’s frescoes.",
 "Marie Louise was a popular ruler in Parma.",
 [B+", “Parma”"])
add("ritzebuttel",["Cuxhaven"],"Ritzebüttel (Cuxhaven)","Hamburg exclave","1394–1937",
 "Ritzebüttel was Hamburg’s exclave at the mouth of the Elbe, including Cuxhaven. Hamburg held it from 1394 until 1937.",
 "Napoleonic occupation.",
 "Hamburg’s appointed governors (Amtmänner).",
 "Lutheran.",
 "A harbour and pilot station.",
 "Cuxhaven was Hamburg’s outport.",
 [B+", “Cuxhaven”"])
add("persia-qajar",["Persia"],"Persia (Zand and Qajar)","monarchy","Zand 1751–1794; Qajar 1789/96–1925",
 "In 1789 Persia was moving from the Zand dynasty to the Qajars, who ruled until 1925. Russia took Persia’s Caucasus lands in the treaties of Gulistan (1813) and Turkmenchay (1828). The Constitutional Revolution of 1906 created a parliament.",
 "Russo-Persian wars; the Anglo-Russian convention of 1907.",
 "Agha Mohammad Khan; Fath-Ali Shah; Naser al-Din Shah.",
 "Twelver Shi‘i Islam.",
 "Persian court culture.",
 "Russia and Britain divided Persia into spheres of influence in 1907.",
 [B+", “Qajar dynasty”"])
add("central-asian-khanates",["central Asian khanates"],"Khanates beyond Russia’s frontier","khanates","—",
 "The basemap uses this generic label in 1789 for the Muslim khanates on Russia’s southern frontier: the Kazakh hordes on the steppe and small khanates of the Caucasus and Central Asia (Bukhara, Khiva and Kokand). Russia conquered most of them in the 1800s.",
 "Russian expansion.",
 "Khans of each state.",
 "Sunni Islam.",
 "Nomadic and oasis cultures.",
 "Russia annexed the Caucasus khanates first and the Central Asian ones later.",
 [B+", “Bukhara, khanate of”"])
G=["modern:1815"]
def de(id,n,name,typ,years,summ,lead,story,rel="Lutheran and Reformed Protestant."):
    add(id,[n],name,typ,years,summ,"Napoleonic wars; joined the German Confederation in 1815.",lead,rel,"A small German court culture.",story,[B,"T. Nipperdey, Germany from Napoleon to Bismarck (1996)"],when=G)
de("palatinate","Palatinate","Bavarian Palatinate","Bavarian province","1816–1945","The Palatinate on the left bank of the Rhine. Austria and Bavaria jointly administered it in 1815, and it went to Bavaria in 1816.","Kings of Bavaria.","The Hambach Festival of 1832 was a democratic rally held here.","Catholic and Protestant.")
de("hohenzollern","Hohenzollern","Hohenzollern principalities","principalities","to 1850","The Swabian principalities of Hohenzollern-Hechingen and Hohenzollern-Sigmaringen. They passed to Prussia in 1850.","The Catholic Swabian branch of the Hohenzollerns.","Romania’s Carol I came from the Sigmaringen line.","Catholic.")
de("meck-strelitz","Mecklenburg-Strelitz","Grand Duchy of Mecklenburg-Strelitz","grand duchy","1815–1918","A small north German state that became a grand duchy in 1815.","Grand dukes of Mecklenburg-Strelitz.","Queen Louise of Prussia was born a princess of this house.")
de("hesse-darmstadt","Grand Duchy of Hesse","Grand Duchy of Hesse","grand duchy","1806–1918","Hesse-Darmstadt became a grand duchy in 1806. It added Rhenish Hesse, around Mainz, in 1816 and lasted until 1918.","Louis I, its first grand duke.","Its princesses married into the Russian and British royal families.")
de("nassau","Nassau","Duchy of Nassau","duchy","1806–1866","A duchy on the Rhine and Lahn rivers. Prussia annexed it in 1866.","Dukes of Nassau.","Its last duke, Adolphe, later became Grand Duke of Luxembourg.")
de("wetzlar","Wetzlar","Wetzlar","Prussian exclave","Prussian from 1815","Wetzlar was a former imperial city and the seat of the Imperial Chamber Court from 1689 to 1806. It became a Prussian exclave in 1815.","Prussian officials.","Goethe worked at the court here in 1772, which inspired The Sorrows of Young Werther.")
de("waldeck","Waldeck","Principality of Waldeck","principality","to 1918","A small Hessian principality, also called Waldeck-Pyrmont.","Princes of Waldeck.","Its princes served as commanders in many European armies.")
de("lippe","Lippe-Detmold","Principality of Lippe","principality","to 1918","A principality in Westphalia, ruled from Detmold.","Princes of Lippe.","The Hermann Monument near Detmold was finished in 1875.")
de("brunswick","Brunswick","Duchy of Brunswick","duchy","1814–1918","A Guelph duchy in Lower Saxony.","Frederick William, the ‘Black Duke’, killed at Quatre Bras (1815).","The Black Duke’s ‘Black Brunswickers’ fought Napoleon.")
de("anhalt","Anhalt","Anhalt duchies","duchies","to 1863 (then united)","The duchies of Anhalt-Dessau, Köthen and Bernburg. They were united as one duchy in 1863.","Leopold IV of Anhalt-Dessau.","The Dessau-Wörlitz Garden Realm is a World Heritage Site.")
de("meck-schwerin","Mecklenburg-Schwerin","Grand Duchy of Mecklenburg-Schwerin","grand duchy","1815–1918","A Baltic grand duchy, one of the most feudal and conservative states in Germany.","Frederick Francis I.","Landowning estates dominated the duchy until 1918.")
de("thuringia","Thuringia","Thuringian states","duchies and principalities","to 1920","The basemap groups the small Thuringian states under one label. They included Saxe-Weimar-Eisenach, which became a grand duchy in 1815, the Saxon duchies, Schwarzburg and Reuss. They were merged into the state of Thuringia in 1920.","Charles Augustus of Saxe-Weimar.","Goethe and Schiller made Weimar Germany’s literary capital.")
for id,n,yrs,story in [("lubeck","Lübeck","to 1937","Lübeck was once the leading city of the Hanseatic League."),("bremen","Bremen","to present (as a state)","Bremen is still a city-state of Germany today."),("hamburg","Hamburg","to present (as a state)","Hamburg is still a city-state of Germany today.")]:
    add(id,[n],"Free City of "+n,"free city",yrs,f"{n} was a free Hanseatic city and became a sovereign member of the German Confederation in 1815.","French annexation (1810–1813).","An elected senate and burgomasters.","Lutheran.","Merchant republic culture.",story,[B+f", “{n}”"],when=G)
de("oldenburg","Oldenburg","Grand Duchy of Oldenburg","grand duchy","1815–1918","Oldenburg was raised to a grand duchy at Vienna in 1815, though its rulers only adopted the title in 1829.","Peter I.","The ruling house was related to the Russian imperial family.")
de("hesse-kassel","Electoral Hesse","Electorate of Hesse (Hesse-Kassel)","electorate","1803–1866","Its ruler kept the title of Elector even after the Holy Roman Empire ended. Prussia annexed it in 1866.","William I.","The Brothers Grimm worked in Kassel.")
de("schaumburg-lippe","Schaumburg-Lippe","Principality of Schaumburg-Lippe","principality","to 1918","One of the smallest German states, ruled from Bückeburg.","Prince George William.","Its tiny army was famous in the 1700s.")
add("lucca",["Lucca"],"Duchy of Lucca","duchy","1815–1847","A duchy created at the Congress of Vienna for the Bourbon-Parma family. It was merged into Tuscany in 1847.","Upheavals of 1847.","Maria Luisa of Bourbon; Charles Louis.","Catholic.","A walled Tuscan city.","Lucca’s Renaissance walls survive intact.",[B+", “Lucca”"],when=G)
add("massa",["Massa"],"Duchy of Massa and Carrara","duchy","to 1829 (then Modena)","A small duchy on the Tuscan coast, famous for its Carrara marble. It went to Modena in 1829.","Napoleonic era.","Maria Beatrice d’Este.","Catholic.","Marble quarrying.","Michelangelo chose marble at Carrara.",[B+", “Massa”"],when=G)
add("krakow",["Republic of Kraków"],"Free City of Kraków","free city","1815–1846","A free city under the joint protection of Austria, Prussia and Russia, created in 1815. Austria annexed it after the uprising of 1846.","Kraków Uprising (1846).","An elected senate.","Catholic.","Polish university life.","It was the last independent Polish territory before 1918.",[B+", “Kraków”"],when=G)
add("san-marino",["San Marino"],"Republic of San Marino","republic","c. 301 (traditional)–present","A tiny mountain republic. The Congress of Vienna confirmed its independence.","It sheltered Garibaldi in 1849.","Captains Regent.","Catholic.","Mount Titano.","It claims to be the world’s oldest republic.",[B+", “San Marino”"])
add("georgia-1914",["Georgia"],"Georgia (Russian Empire)","imperial governorates","Russian 1801–1917","In 1914 Georgia was ruled by the Russian Empire as the Tiflis and Kutaisi governorates. Russia had annexed Kartli-Kakheti in 1801.","World War I on the Caucasus front.","Russian viceroys.","Georgian Orthodox Church.","Tiflis was the region’s cultural capital.","Georgia declared independence in 1918.",[B+", “Georgia: History”"],when=["modern:1914"])
add("armenia-1914",["Armenia"],"Russian Armenia","imperial governorate","Russian 1828–1917","In 1914 the Erivan governorate was the Armenian part of the Russian Empire.","The Ottoman genocide of Armenians (1915).","Russian governors.","Armenian Apostolic Church.","The Armenian church centre of Etchmiadzin.","Armenia declared independence in 1918.",[B+", “Armenia: History”"],when=["modern:1914"])
add("azerbaijan-1914",["Azerbaijan"],"Azerbaijan (Russian Empire)","imperial governorates","Russian 1813/28–1917","In 1914 the Baku and Elisabethpol governorates were part of the Russian Empire. Baku’s oilfields were among the largest in the world.","Revolution of 1905.","Russian governors.","Shi‘i Islam.","Baku oil wealth.","Azerbaijan declared independence in 1918.",[B+", “Azerbaijan: History”"],when=["modern:1914"])
add("iceland-1914",["Iceland"],"Iceland","Danish dependency","home rule 1904; sovereign 1918; republic 1944","In 1914 Iceland had home rule under Denmark. It became a sovereign kingdom in personal union with Denmark in 1918 and a republic in 1944.","None.","Hannes Hafstein, the first minister.","Lutheran.","Saga heritage.","The Althing is one of the oldest parliaments in the world.",[B+", “Iceland”"],when=["modern:1914"])
add("malta",["Malta"],"Malta","British colony, then republic","British 1800–1964; republic 1974","Malta was a British naval base from 1800 and became independent in 1964. It joined the EU in 2004.","Siege of Malta (1940–1942).","Dom Mintoff.","Catholic.","Maltese language.","The whole island received the George Cross in 1942.",[B+", “Malta”"])
add("iran-20c",["Iran"],"Iran","monarchy, then Islamic republic","Pahlavi 1925–1979; Islamic Republic 1979–","In 1945 Iran was ruled by the Pahlavi shahs, after the Allied occupation of 1941. The 1979 revolution created the Islamic Republic.","Iran–Iraq War (1980–1988).","Mohammad Reza Shah; Khomeini.","Shi‘i Islam.","Persian culture.","The Tehran Conference was held there in 1943.",[B+", “Iran”"])
add("iraq-20c",["Iraq"],"Iraq","kingdom, then republic","kingdom 1932–1958; republic 1958–","Iraq was a monarchy until the revolution of 1958. From 1968 the Ba‘ath party ruled it, under Saddam Hussein from 1979.","Iran–Iraq War; Gulf War (1991).","Faisal I; Saddam Hussein.","Islam.","Mesopotamian heritage.","Iraq became independent in 1932.",[B+", “Iraq”"])
add("syria-20c",["Syria"],"Syria","mandate, then republic","French mandate to 1946; republic 1946–","Syria came out of the French mandate in 1946. The Ba‘ath party took power in 1963, and Hafez al-Assad ruled from 1970.","Arab–Israeli wars.","Hafez al-Assad.","Sunni Islam with minorities.","Damascus and Aleppo.","Syria joined Egypt in the United Arab Republic (1958–1961).",[B+", “Syria”"])
add("andorra",["Andorra"],"Andorra","co-principality","1278–present","A Pyrenean co-principality ruled jointly by the Bishop of Urgell and the French head of state. It adopted a constitution in 1993.","None.","Co-princes.","Catholic.","Catalan language.","The 1278 pareatges agreement still underpins the arrangement.",[B+", “Andorra”"])
add("liechtenstein",["Liechtenstein"],"Liechtenstein","principality","1719–present","A small Alpine principality, in a customs union with Switzerland since 1923.","None.","Princes of Liechtenstein.","Catholic.","Banking.","It has had no army since 1868.",[B+", “Liechtenstein”"])
add("kazakhstan",["Kazakhstan"],"Kazakhstan","republic","1991–present","Kazakhstan became independent from the USSR in 1991. It is the largest landlocked country in the world.","None.","Nursultan Nazarbayev.","Islam and Orthodox Christianity.","Kazakh and Russian languages.","The Baikonur Cosmodrome is in Kazakhstan.",[B+", “Kazakhstan”"],when=["modern:2000"])
add("georgia-2000",["Georgia"],"Georgia","republic","1991–present","Georgia became independent in 1991. Wars over Abkhazia and South Ossetia followed.","Abkhazia war (1992–1993).","Eduard Shevardnadze.","Georgian Orthodox Church.","Georgian script.","The Rose Revolution came in 2003.",[B+", “Georgia”"],when=["modern:2000"])
add("armenia-2000",["Armenia"],"Armenia","republic","1991–present","Armenia became independent in 1991 and fought Azerbaijan over Karabakh.","Karabakh war (1988–1994).","Levon Ter-Petrosyan.","Armenian Apostolic Church.","Armenian language.","Armenia adopted Christianity as its state religion in 301.",[B+", “Armenia”"],when=["modern:2000"])
add("azerbaijan-2000",["Azerbaijan"],"Azerbaijan","republic","1991–present","Azerbaijan became independent in 1991 and has an oil-based economy.","Karabakh war.","Heydar Aliyev.","Shi‘i Islam.","Azerbaijani language.","Baku is on the Caspian Sea.",[B+", “Azerbaijan”"],when=["modern:2000"])
add("cyprus-2000",["Cyprus"],"Republic of Cyprus","republic","1960–present","Cyprus became independent from Britain in 1960. It has been divided since Turkey’s invasion in 1974.","1974 invasion.","Makarios III.","Greek Orthodox.","Greek and Turkish communities.","Cyprus joined the EU in 2004.",[B+", “Cyprus”"],when=["modern:2000"])
add("north-cyprus",["Turkish Cypriot-administered area"],"Turkish Cypriot-administered area","de facto state","1974/1983–present","The north of Cyprus, under Turkish Cypriot administration since 1974. Only Turkey recognises it.","1974 invasion.","Rauf Denktaş.","Sunni Islam.","Turkish Cypriot community.","A UN buffer zone runs through Nicosia.",[B+", “Cyprus”"],when=["modern:2000"])
import json
json.dump({"note":"Europa Strata profiles for smaller polities and peoples that the historical-basemaps borders name but the main era packs don't profile. Matched by basemap name; `when` limits an entry to tab:year stops. Sources per entry; general reference: Encyclopaedia Britannica.","profiles":P},open(__import__('os').path.join(__import__('os').path.dirname(__file__),'..','data','kingdom-eras','basemap-profiles.json'),'w'),ensure_ascii=False,indent=1)
print(len(P))
