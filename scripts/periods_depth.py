# -*- coding: utf-8 -*-
"""Depth pass for the 'enlightenment' (1750) and 'eve-of-war' (1914) periods.

ADD[pid][iso][field]  -> text appended (after a space) to the polity field.
SET[pid][iso][field]  -> text that replaces the field (used to soften or correct).
IMAGES[pid][iso]      -> full replacement gallery: (Commons file, caption, role).
Applied by add_periods_1750_1914.py after the base data modules are loaded.
"""

ADD = {"enlightenment": {}, "eve-of-war": {}}
SET = {"enlightenment": {}, "eve-of-war": {}}
IMAGES = {"enlightenment": {}, "eve-of-war": {}}
E, W = ADD["enlightenment"], ADD["eve-of-war"]

# ---------------------------------------------------------------- 1750
E["GBR"] = dict(
 culture="Coffee houses, subscription libraries and provincial newspapers make a reading public far beyond London.",
 ideas="Excise and the Bank of England let a small island borrow cheaply for war.")
E["IRL"] = dict(
 summary="Its Parliament in Dublin sits under Poynings’ Law and the Declaratory Act of 1720, so London can override it.",
 conflicts="The Money Bill dispute of 1753–56 pits the Irish Commons, led by Speaker Boyle, against the Lord Lieutenant over who controls a budget surplus.",
 culture="Dublin is the second city of the British Isles, with the Parliament House on College Green (1729–39) and new Georgian squares; in the countryside Irish remains the language of most of the population.",
 story="Outside Dublin, the Penal Laws bar Catholics from Parliament, from most professions and from buying land on long leases, so the Catholic gentry that survived the seventeenth century shrinks year by year through conversion and subdivision.",
 literature="Swift’s Drapier’s Letters (1724–25) had made him a hero of Dublin’s Protestant ‘patriots’; Irish-language poets such as Aogán Ó Rathaille (d. 1729) mourn the fall of the Gaelic aristocracy in the aisling vision poem.",
 art="Turlough O’Carolan’s harp tunes are collected and printed; Edward Lovett Pearce’s Parliament House introduces Palladian architecture on a monumental scale.",
 ideas="Berkeley’s The Querist (1735–37) asks why a fertile country should be so poor, and proposes a national bank and home industry.",
 philosophy="Berkeley’s Treatise (1710) and Three Dialogues (1713) argued that to be is to be perceived; as bishop he writes on tar-water and Irish poverty.",
 science="Trinity College Dublin, the country’s only university, is open in practice to Anglicans; the Dublin Society funds premiums for improved farming, linen and fisheries.")
E["FRA"] = dict(
 story="The volumes keep appearing until 1772, seventeen of text and eleven of plates, with articles by Voltaire, Rousseau, Montesquieu and Quesnay.",
 culture="Paris salons kept by women such as Madame Geoffrin bring philosophes, nobles and foreign visitors together.")
E["ESP"] = dict(
 summary="Ensenada’s plans for a single tax (the catastro of 1749–56) and a rebuilt navy give the reign a reforming centre until his fall in 1754.",
 conflicts="Spain stays neutral in the first years of the Seven Years’ War and enters only in 1762, under Charles III.",
 culture="The Royal Academy of Fine Arts of San Fernando is founded in Madrid in 1752 to train painters, sculptors and architects on academic lines.",
 story="Behind the music is policy: Ferdinand VI and his Portuguese queen, Barbara of Braganza, keep Spain out of war, settle the American border with Portugal and let Ensenada and Carvajal reform the state.",
 literature="Ignacio de Luzán’s Poética (1737) pleads for neoclassical rules in Spanish drama.",
 ideas="Regalism: the crown claims authority over the Spanish church, won in the Concordat of 1753.",
 philosophy="Feijoo, a Benedictine monk in Oviedo, publishes the Teatro crítico universal in eight volumes (1726–39) and the Cartas eruditas (1742–60), urging Spaniards to test beliefs against experience.",
 science="Jorge Juan and Ulloa’s reports of the geodesic mission (1748) are published in Madrid; Juan later studies British shipbuilding and modernises the Spanish dockyards.")
E["PRT"] = dict(
 conflicts="Pombal’s rise is accompanied by the Távora affair (1758–59), when an attempt on the king’s life is used to destroy great noble families and the Jesuits.",
 leaders="Queen Mariana Victoria, Spanish-born consort of Joseph I.",
 culture="Gold from Minas Gerais pays for gilded church interiors, the Aqueduto das Águas Livres (1731–48) in Lisbon and the royal library at Mafra.",
 story="Before the disaster, John V’s court had spent Brazilian gold on Mafra and on buying Rome’s favour; he was rewarded with the papal title ‘Most Faithful Majesty’ (1748). His death in July 1750 brings in his son Joseph I, who lets Carvalho e Melo run the government.",
 literature="The Arcádia Lusitana (1756) gathers poets who want plain classical verse in place of the baroque conceit.",
 art="Gilded woodcarving (talha dourada) and blue-and-white azulejo panels cover church walls; the Águas Livres aqueduct survives the earthquake.",
 ideas="Pombal’s monopoly companies (the Douro wine company, 1756) regulate trade with Britain and Brazil.",
 philosophy="Verney attacks Aristotelian teaching and calls for Portuguese grammar, modern logic and experimental physics.",
 science="Pombal later reforms the University of Coimbra (1772) with laboratories and a botanical garden.")
E["NLD"] = dict(
 summary="Amsterdam is still the capital market of Europe, but Britain and France now outbuild and outfight the Dutch.",
 conflicts="The Doelisten movement in Amsterdam (1748) demands open government and the end of venal offices.",
 leaders="William IV’s widow Anne of Hanover is regent (1751–59), with Duke Louis Ernest of Brunswick as guardian of the young William V.",
 culture="The East and West India Companies, the Amsterdam exchange and the herring and whaling fleets still employ tens of thousands.",
 story="William IV becomes stadtholder of all seven provinces in 1747, the first time one prince has held them all; the office is made hereditary in his line. When he dies in 1751 his son is three years old and the republic is governed by his widow and a guardian.",
 literature="Elie Luzac and Marc-Michel Rey in Leiden and Amsterdam publish La Mettrie, Rousseau and others who cannot print freely in France.",
 art="Cornelis Troost (d. 1750), the ‘Dutch Hogarth’, paints theatre and comic scenes; Delft factories produce tin-glazed earthenware in imitation of Chinese porcelain.",
 ideas="The Orangist revolution of 1747–48 is the first sign of the Patriot–Orangist conflict that will split the republic in the 1780s.",
 philosophy="Leiden and Utrecht teach Newton through ’s Gravesande (d. 1742) and Musschenbroek, making the republic a channel for English science to the continent.",
 science="Musschenbroek’s Leyden jar is the first device to store an electric charge; its shock becomes the sensation of salons across Europe.")
E["BEL"] = dict(
 summary="Governed from Brussels by Charles of Lorraine, Maria Theresa’s brother-in-law, they enjoy thirty years of peace after 1748.",
 conflicts="The Barrier Treaty forces the provinces to pay for Dutch garrisons in their own fortresses; Joseph II ends it in 1781.",
 culture="Charles of Lorraine’s court, his palace in Brussels (rebuilt from 1757) and the theatre of La Monnaie make Brussels a small capital of French taste.",
 story="When the French withdraw, Charles of Lorraine returns to a country that has been fought over for a century. His governorship (1744–80) is remembered as a golden age: canals and roads are built, Ostend and Bruges are linked to the hinterland, and Brussels is rebuilt in a sober classicism.",
 literature="Brussels printers and the Leuven faculty serve a Catholic, largely French-reading elite; Flemish is spoken in the countryside and the towns of Flanders and Brabant.",
 art="Brussels tapestry workshops still weave for European courts; the Coudenberg area is redesigned as Place Royale in the 1770s.",
 ideas="Vienna’s ministers (Cobenzl, later Starhemberg) push cautious Catholic Enlightenment reforms; the provincial estates resist any loss of their charters.",
 philosophy="Leuven remains loyal to Jansenist-tinged Augustinian theology even after the papal condemnations.",
 science="Charles of Lorraine collects natural history and instruments; the Imperial and Royal Academy of Brussels follows in 1772.")
E["DEU"] = dict(
 culture="Courts at Dresden, Munich, Mannheim and Würzburg compete in opera, porcelain (Meissen, Nymphenburg) and palace building.")
E["AUT"] = dict(
 summary="Haugwitz’s reforms of 1749 merge the Austrian and Bohemian chancelleries and fund a standing army of over 100,000 men from regular taxes voted for ten years at a time.",
 culture="Gluck, Wagenseil and the young Haydn work in a city whose music is paid for by court, church and nobility.",
 story="The new course is meant to fight Prussia with Prussian methods: Kaunitz in diplomacy, Haugwitz in finance and Daun in the army, which wins at Kolín in 1757.",
 literature="Joseph von Sonnenfels and the Viennese press soon argue for a German-language Enlightenment.",
 science="The Theresianum (1746) trains officials; Van Swieten modernises the court library and the University of Vienna’s medical faculty.")
E["CZE"] = dict(
 summary="Prague is a provincial capital, but Bohemian glass, linen and the textile industries of northern Bohemia make the region one of the monarchy’s richest.",
 conflicts="In 1757 Frederick II besieges Prague and is beaten at Kolín (18 June) by Daun’s Austrian army.",
 culture="Baroque churches and pilgrimage sites, such as the Kilian Ignaz Dientzenhofer and Santini buildings, cover the countryside after the Counter-Reformation.",
 story="The reform hits the Bohemian nobility’s self-government but not its lordship over the peasants: the robot labour dues that tie Czech villages to their manors remain until 1848.",
 literature="Jesuit hagiography and baroque hymnals (the Svatováclavský sborník) keep Czech in print; German is the language of administration and the universities.",
 art="The Clementinum’s baroque library hall (1720s) and St Nicholas in the Lesser Town, finished in the 1750s, are high points of Prague baroque.",
 ideas="The Theresian cadastre of 1748 records noble and peasant land for taxation.",
 philosophy="The Jesuit Clementinum dominates the Charles-Ferdinand University until the order is suppressed in 1773.",
 science="Diviš, a Premonstratensian priest, raises his grounded ‘weather machine’ at Přímětice in Moravia on 15 June 1754; villagers later pull it down, blaming it for drought.")
E["HUN"] = dict(
 summary="After 1711 the Peace of Szatmár leaves the nobility its tax exemption in exchange for loyalty to the dynasty.",
 conflicts="Hungarian hussars and the noble levy serve in the Silesian wars; Hungarian regiments fight in the Seven Years’ War.",
 leaders="Count Lajos Batthyány (palatine 1751–65); Antal Grassalkovich, president of the Hungarian Chamber.",
 culture="German, Serbian, Slovak and Romanian settlers repopulate the southern plain; Pressburg (Pozsony, now Bratislava) is the seat of the Diet and the coronation city.",
 story="The nobles’ loyalty has a price: the Diet of 1741 confirms their exemption from taxation and the separate Hungarian administration. Maria Theresa calls the Diet only twice more (1751 and 1764–65) and governs Hungary through decrees and the Hungarian Chancellery in Vienna.",
 literature="Mátyás Bél, a Lutheran pastor in Pressburg, publishes his Notitia Hungariae novae historico-geographica (1735–42), a county-by-county description of the kingdom in Latin.",
 art="Baroque churches and palaces rise in Eger, Gödöllő (the Grassalkovich palace, from c. 1741) and Pressburg Castle, rebuilt for the queen.",
 ideas="The ‘Hungarian constitution’ means noble privilege: the Diet votes taxes on peasants only.",
 philosophy="Jesuit Nagyszombat (Trnava) university; the Reformed colleges of Debrecen and Sárospatak.",
 science="Bél’s survey also maps the kingdom’s mines, rivers and towns; Selmecbánya (Banská Štiavnica) mining school is founded in the 1760s.")
E["CHE"] = dict(
 summary="The cantons sit in the Diet as allies, not as a state; subject territories such as Vaud (ruled by Bern) and the Ticino bailiwicks have no say.",
 conflicts="Samuel Henzi and his fellow conspirators in Bern, who wanted to open the patrician government to more burghers, are executed in 1749.",
 leaders="Bern’s patrician families (von Steiger, von Erlach); Zurich’s guild oligarchy.",
 culture="Geneva and Neuchâtel are centres of printing and watchmaking; Basel, Bern and Zurich produce silk, cotton and banking.",
 story="Rousseau’s prize essay is printed in Geneva’s shadow: the city, a Calvinist republic allied with the Confederacy, is itself divided between a ruling Petit Conseil and citizens who want more power.",
 literature="Haller’s Die Alpen praises the virtuous poverty of Alpine herdsmen; Bodmer translates Milton into German (1732).",
 art="Watchmakers in the Jura and Geneva; Jean-Étienne Liotard, the Genevan pastellist, works across Europe.",
 ideas="Jean-Jacques Burlamaqui’s Principes du droit naturel (1747) is read by later constitution makers.",
 philosophy="Burlamaqui and later Vattel (The Law of Nations, 1758) give Swiss natural law a European audience.",
 science="Daniel Bernoulli moves back to Basel in 1733; Haller, professor at Göttingen 1736–53, returns to Bern and writes his Elementa physiologiae (1757–66).")
E["ITA"] = dict(
 culture="Opera seria, the castrato voice and Neapolitan conservatories spread Italian music across Europe.")
E["POL"] = dict(
 summary="Augustus III spends most of his reign in Dresden; government rests with the great magnate families and the regional sejmiks.",
 conflicts="The Commonwealth stays formally neutral in the Seven Years’ War while Russian armies march through it to fight Prussia.",
 leaders="Prince-Primate and the Załuski bishops; Stanisław Konarski, Piarist reformer.",
 culture="Noble manor houses, Sarmatian dress, Latinised speech and Catholic baroque piety; Jews are a large share of the population of many towns.",
 story="Konarski opens his Collegium Nobilium for young nobles in Warsaw in 1740, teaching modern languages, history and natural science: the first step towards the reforms of the 1760s–90s.",
 literature="Konarski’s Volumina Legum (from 1732) publishes the Commonwealth’s laws in print for the first time.",
 art="Saxon court architects in Warsaw; Bellotto, nephew of Canaletto, works in Dresden in the 1750s before moving to Warsaw in 1767.",
 ideas="Golden Liberty (free election, liberum veto, the right of confederation) against Familia plans for a stronger executive.",
 philosophy="Piarist schools take on Locke and the new science; the Jesuit academies adapt.",
 science="The Załuski brothers, both bishops, open their library to the public in 1747, with hundreds of thousands of volumes.")
E["LTU"] = dict(
 summary="Its own treasury, army and laws (the Third Lithuanian Statute of 1588) survive under the common crown.",
 conflicts="Radziwiłł and Sapieha clients fight over the Lithuanian Tribunal and offices.",
 culture="Lithuanian-speaking peasants live in serfdom under Polish-speaking lords; Belarusian (Ruthenian) speakers fill the east.",
 story="Fires in 1737, 1748 and 1749 destroy much of Vilnius; the Jesuits, the Orthodox and the Uniate orders rebuild in the late baroque that gives the ‘Vilnius baroque’ school its name. Elijah ben Solomon, the Vilna Gaon, opposes the Hasidic movement spreading from Podolia.",
 literature="The Lithuanian Lutheran pastor Kristijonas Donelaitis writes The Seasons (Metai, 1760s) in Prussian Lithuania.",
 art="Glaubitz rebuilds St Catherine’s and the Church of the Holy Spirit; the Radziwiłł court at Nieśwież has its own theatre.",
 ideas="The Lithuanian magnates use the Commonwealth’s liberties against both king and Russia, but often in alliance with Russia.",
 philosophy="The Jesuit Academy of Vilnius, the oldest university in the Commonwealth’s east (1579).",
 science="The observatory of Vilnius University is founded in 1753, the oldest in the region.")
E["UKR"] = dict(
 conflicts="The New Serbia settlement (1752) on the southern steppe plants Balkan colonists under Russian command on Zaporozhian land.",
 leaders="Grigory Teplov, Rozumovsky’s adviser.",
 culture="The Zaporozhian Host keeps its own Sich on the lower Dnieper under Russian protection since 1734; south of it are the Crimean khans’ Nogai steppes.",
 story="In Hlukhiv the young hetman tries to restore Cossack courts and a capital fit for a court, and even plans a university in Baturyn; St Petersburg allows the pageantry but tightens its hold on taxes and appointments.",
 literature="Skovoroda studies at the Kyiv-Mohyla Academy and travels abroad (1745–50) before beginning his wandering life.",
 art="Cossack baroque churches with pear-shaped domes; the Kyiv Pechersk Lavra bell tower (1731–45).",
 ideas="The Hetmanate’s autonomy rests on Bohdan Khmelnytsky’s treaty of 1654, which Russia reinterprets as submission.",
 philosophy="Skovoroda’s ethics of self-knowledge and ‘congenial labour’ are written down from the 1760s.",
 science="The Kyiv-Mohyla Academy, with over a thousand students at its height, trains clergy and officials for the whole Russian Empire.")
E["RUS"] = dict(
 conflicts="Russian troops occupy East Prussia (1758) and briefly Berlin (1760) in the Seven Years’ War.",
 culture="Elizabeth abolishes the death penalty in practice and fills her palaces with Italian architects and French actors.",
 story="Lomonosov is a chemist, a mosaicist and a poet: he sets up a glassworks for mosaics, writes odes to Elizabeth and argues with German academicians about the origins of the Russian state.",
 art="Ivan Argunov, a serf painter of the Sheremetevs, paints portraits; the Academy of Arts is founded in 1757.",
 ideas="Noble privileges grow while serfdom deepens; the 1754 abolition of internal customs creates a single market.",
 philosophy="Lomonosov’s natural philosophy and his theory of Russian style (high, middle and low).",
 science="The St Petersburg Academy (1724) employs Euler (to 1741 and again from 1766), Daniel Bernoulli and Lomonosov; the Academy’s expeditions map Siberia.")
E["SWE"] = dict(
 summary="The Hats, a party of merchants and officers, dream of revenge on Russia and support manufactures with subsidies.",
 conflicts="Queen Louisa Ulrika, Frederick II’s sister, attempts a royal coup in 1756 and fails; several courtiers are executed.",
 culture="The Royal Swedish Academy of Sciences (1739) and the Uppsala botanical garden make Sweden a scientific power.",
 story="Linnaeus’s pupils travel to China, Arabia, North America and Japan; Pehr Kalm goes to North America, Pehr Osbeck to China, Peter Forsskål to Arabia, and many never return.",
 literature="Hedvig Charlotta Nordenflycht, the first Swedish woman to live by her pen, publishes her poems from 1744.",
 art="Gustaf Lundberg’s pastels and the court rococo of Hårleman; Drottningholm’s palace and gardens.",
 ideas="The 1766 Freedom of the Press Act, the first in the world, comes out of these Riksdag debates.",
 philosophy="Swedenborg turns from mining science to visions, publishing Arcana Coelestia (1749–56) in London.",
 science="Celsius’s centigrade scale (1742), reversed after his death to its modern form; Christopher Polhem’s mechanics; Pehr Wargentin’s population statistics.")
E["FIN"] = dict(
 summary="The Treaty of Åbo (1743) moves the border west to the Kymi river, leaving Savonlinna and Lappeenranta in Russian hands.",
 conflicts="During the ‘Lesser Wrath’ (1742–43) Russian troops occupy all of Finland.",
 leaders="Bishops of Turku; Augustin Ehrensvärd, who directs the fortress works from 1748.",
 culture="Turku (Åbo) is the main town, seat of the bishop and the Academy; Helsinki is a small town of about 1,500 people until the fortress work brings soldiers and craftsmen.",
 story="The Swedish Diet of 1747 approves a plan for a great fortress and naval base off Helsinki and a frontier fortress at Degerby (Loviisa). Thousands of soldiers work on the islands; in 1750 the fortress is named Sveaborg, ‘Fortress of Sweden’. Sweden’s largest building project of the century is never quite finished.",
 literature="Daniel Juslenius’s Finnish dictionary (1745) and patriotic histories praise the Finnish language.",
 art="Ehrensvärd, also a draughtsman, designs the fortress gate and courtyards himself.",
 ideas="Finland as the shield of the Swedish realm against Russia.",
 philosophy="The Academy of Turku, founded in 1640, teaches in Latin and Swedish; Henrik Gabriel Porthan begins his studies there in the 1750s.",
 science="Kalm, appointed professor at Turku, brings back North American plants and describes Niagara Falls in his Travels.")
E["DNK"] = dict(
 summary="The monarchy draws large revenues from the Sound Dues paid by every ship entering the Baltic.",
 conflicts="Copenhagen buys peace: Denmark–Norway stays out of the Seven Years’ War and bargains with Russia over the Gottorp lands in Holstein.",
 culture="The Royal Danish Academy of Fine Arts is founded in 1754; the Royal Theatre opens in Kongens Nytorv in 1748.",
 story="Eigtved’s four Amalienborg palaces, built for noble families, frame an octagonal square; at its centre Moltke’s Asiatic Company pays for Jacques Saly’s equestrian statue of Frederick V, unveiled in 1771. Frederiks Church, planned at the same time, is completed only in 1894.",
 literature="Holberg, born in Bergen and professor in Copenhagen, writes some thirty comedies for the Danish stage (Jeppe of the Hill, 1722) and is made a baron in 1747.",
 art="Nicolai Eigtved’s rococo; Carl Gustaf Pilo, court painter.",
 ideas="The Royal Law of 1665 makes the king absolute; officials of the Danish chancellery and German Chancellery govern the realm.",
 philosophy="Holberg’s moral essays and his satirical novel Niels Klim (1741).",
 science="The Danish Academy of Sciences, founded in 1742, begins the mapping of the kingdom.")
E["NOR"] = dict(
 summary="Norway has its own laws (Christian V’s Norwegian Law, 1687) and army but no university, so its officials study in Copenhagen.",
 conflicts="The Strömstad treaty ends a century of uncertainty along the northern border, the longest in Europe.",
 leaders="Stattholders in Christiania; Bishop Erik Pontoppidan of Bergen (1747–54).",
 culture="Timber from the south-east, stockfish from the north, and Røros and Kongsberg mines; farmers own much of their land, unlike Danish peasants.",
 story="The border treaty was signed in Strömstad on 21 September and 2 October 1751. Its first codicil, the Lapp Codicil, lets Sámi herders move their reindeer across the border in spring and autumn ‘according to ancient custom’, even in time of war—a clause still cited in border grazing disputes today.",
 literature="Pontoppidan’s Natural History of Norway (1752–53) describes fjords, sea serpents and the kraken.",
 art="Rose painting spreads through farm interiors from the mid-century; church woodcarving in acanthus style.",
 ideas="Officials, merchants and farmers start to speak of Norway’s separate interests within the union.",
 philosophy="Holberg’s Bergen birth gives Norway a share in the Dano-Norwegian Enlightenment.",
 science="Kongsberg silver mines, the largest industrial enterprise in the realm; Røros copper works.")
E["TUR"] = dict(
 conflicts="Russia’s defeat at Prut (1711) and Austria’s loss of Belgrade (1739) make the Ottomans feel secure in Europe until the war of 1768–74.",
 culture="Istanbul’s coffee houses, public fountains and Bosporus palaces; Tulip-era tastes linger at court.",
 story="Mahmud I’s long peace in Europe lets the empire rebuild its capital, but the provinces are run by ayan families who collect taxes and raise their own troops.",
 literature="Müteferrika’s press prints histories, dictionaries and geographies until 1742; the poet Şeyh Galip is born in 1757.",
 art="European motifs—acanthus, scrolls, curved cornices—appear on mosques and fountains; the Laleli mosque follows in 1760–63.",
 ideas="Claude-Alexandre de Bonneval, a French convert, reorganises the bombardier corps (1730s).",
 philosophy="Müteferrika’s own essay on the reform of the army and state (1732).",
 science="The press’s maps and Kâtip Çelebi’s geography Cihannüma (printed 1732).")
E["GRC"] = dict(
 summary="The Ionian islands remain Venetian; Greek shipowners on Hydra, Spetses and Psara are beginning to build merchant fleets.",
 conflicts="Local revolts and klephts in the mountains; the Morea (Peloponnese) has been Ottoman again since 1715.",
 culture="Greek merchant colonies in Venice, Vienna, Trieste and Smyrna pay for schools and books.",
 story="Voulgaris, born in Corfu and educated in Padua, gives the Academy a curriculum of classical philology, modern philosophy, mathematics and physics; conservative opposition forces him out in 1759, and he moves to the Patriarchal Academy in Constantinople.",
 literature="Greek books are printed in Venice by the Glykis and Saros houses; Nikodemos the Hagiorite is born on Naxos in 1749.",
 art="Post-Byzantine icon painting on Athos and in the Ionian school; British antiquaries Stuart and Revett draw the monuments of Athens (1751–53).",
 ideas="The Phanariot families of Constantinople serve the sultan as dragomans and princes of the Danubian principalities.",
 philosophy="Voulgaris teaches Descartes, Leibniz, Wolff and Locke alongside Aristotle.",
 science="The Athonite Academy’s mathematics and physics; Greek translations of Western textbooks.")
E["ROU"] = dict(
 summary="The princes buy their thrones in Constantinople and are moved between Bucharest and Iași every few years.",
 conflicts="Austro-Ottoman wars repeatedly cross Oltenia (Austrian 1718–39).",
 leaders="Grigore II Ghica; in Transylvania, the Habsburg governor and the Greek Catholic bishop Inochentie Micu-Klein (exiled to Rome in 1744).",
 culture="Boyars wear Ottoman dress and speak Greek at court; peasants speak Romanian; Saxon and Hungarian towns dominate Transylvania.",
 story="The reform let peasants move between estates in exchange for a fixed fee and fixed labour days; it was meant to stop them fleeing across the mountains. In Transylvania, by contrast, Romanian peasants remain serfs and their Orthodox church is not recognised as one of the ‘received’ religions.",
 literature="Dimitrie Cantemir’s Descriptio Moldaviae (written 1714–16) and his history of the Ottoman Empire circulate in Europe.",
 art="Brâncovenesc architecture, after Constantin Brâncoveanu (d. 1714), at Horezu and in Bucharest’s monasteries.",
 ideas="Micu-Klein petitions the Diet and Vienna to recognise Romanians as a fourth nation of Transylvania.",
 philosophy="The princely academies at Bucharest and Iași teach in Greek.",
 science="Greek-language academies teach Aristotelian and, later, Newtonian natural philosophy.")
E["SRB"] = dict(
 summary="North of the Danube, Serbs settle as soldier-peasants on the Military Frontier with religious privileges granted by Leopold I (1690).",
 conflicts="Austria held Belgrade and northern Serbia in 1718–39 before losing them back to the Ottomans.",
 leaders="Arsenije IV Jovanović Šakabenta (patriarch, then metropolitan of Karlovci, d. 1748); Pavle Nenadović (metropolitan of Karlovci 1749–68).",
 culture="Monasteries of Fruška Gora and the Karlovci metropolitanate preserve Serbian Orthodox culture under Habsburg rule.",
 story="Arsenije IV’s flight in 1737–39 follows the first great migration of 1690 under Arsenije III. In the Habsburg lands, Karlovci becomes the seat of Serbian church and school life; the Cathedral of St Nicholas is built there in 1758–62.",
 literature="Hristofor Žefarović’s engraved Stemmatographia (Vienna, 1741) celebrates the South Slav past; Zaharija Orfelin begins the Slaveno-Serbian Magazine in 1768.",
 art="Žefarović’s engravings and frescoes; baroque iconostases in Karlovci and Novi Sad.",
 ideas="The ‘Illyrian privileges’: Serbian self-government in religion and schooling within the Habsburg Monarchy.",
 philosophy="Church schools in Karlovci teach Latin and Church Slavonic with Russian teachers.",
 science="Learning moves north with the migrants.")
SET["enlightenment"] = {
 "SRB": {"science": "Learning moves north with the migrants: Serbian schools at Sremski Karlovci (the gymnasium founded in 1791) grow from the church culture of the Habsburg Serbs."},
}

# ---------------------------------------------------------------- 1914
W["GBR"] = dict(
 culture="Mass-circulation newspapers (the Daily Mail), the music hall and professional football; the suffragettes’ campaign of window-smashing and arson reaches its peak in 1913–14.",
 story="On the 5th the British Expeditionary Force begins crossing to France; it fights at Mons on 23 August.")
W["IRL"] = dict(
 summary="Ulster unionists, armed since 1913, threaten to resist Home Rule by force.",
 culture="The Abbey Theatre (1904), the Gaelic League (1893) and the GAA (1884) build an Irish cultural nation.",
 story="In the Curragh incident of March 1914 British officers say they will resign rather than coerce Ulster; in April unionists land 25,000 rifles at Larne, and in July the Irish Volunteers land their own at Howth.",
 literature="Lady Gregory and Yeats run the Abbey; Joyce’s Dubliners is published in June 1914.",
 art="Harry Clarke begins his stained glass; the Hugh Lane Gallery controversy (1913).",
 ideas="Arthur Griffith’s Sinn Féin and the Irish Republican Brotherhood argue for full separation.",
 philosophy="Patrick Pearse writes on education and blood sacrifice.",
 science="Belfast is an industrial city of shipyards, ropeworks and linen mills.")
W["ESP"] = dict(
 summary="Politics rotates between Conservatives and Liberals under the turno system; anarchists assassinate Prime Minister José Canalejas in 1912.",
 conflicts="The disaster at the Barranco del Lobo near Melilla (July 1909) and the protectorate over northern Morocco (1912).",
 leaders="Antonio Maura (Conservative leader); the Count of Romanones.",
 culture="The Catalan Mancomunitat (1914) gives Catalonia limited self-government.",
 story="When war breaks out, Spain declares neutrality and its factories and mines profit from Allied orders.",
 literature="Valle-Inclán, Pío Baroja and Azorín of the Generation of ’98.",
 art="Picasso and Juan Gris in Paris; Joaquín Sorolla’s light-filled seascapes.",
 ideas="Joaquín Costa’s ‘school and larder’ regenerationism.",
 science="Ramón y Cajal’s neuron doctrine shows that the nervous system is made of separate cells; he shares the 1906 Nobel Prize with Golgi.")
W["PRT"] = dict(
 summary="Governments change almost every few months; the Democratic Party of Afonso Costa dominates.",
 conflicts="The Republic sends troops to defend Angola and Mozambique against German incursions in 1914.",
 leaders="Bernardino Machado (Prime Minister 1914).",
 culture="Republican Lisbon secularises schools, legalises divorce and expels the Jesuits (1910).",
 story="The revolution begins on 3–4 October 1910 with mutinies in the navy and army; the republic is proclaimed from the balcony of Lisbon’s city hall on 5 October.",
 literature="Pessoa, who has returned from Durban in 1905, invents his heteronyms Alberto Caeiro, Ricardo Reis and Álvaro de Campos in 1914.",
 art="Souza-Cardoso shows at the Armory Show in New York (1913).",
 ideas="Anticlericalism and positivism; the 1911 Constitution.",
 philosophy="Teófilo Braga, philosopher and literary historian, provisional president (1910–11) and president (1915).",
 science="The University of Lisbon and the University of Porto are founded in 1911.")
W["NLD"] = dict(
 summary="Wilhelmina reigns over a country of pillarised churches and parties, and over the Dutch East Indies.",
 conflicts="The Netherlands mobilises on 31 July 1914 and receives around a million Belgian refugees in October.",
 culture="Berlage’s Stock Exchange in Amsterdam (1903) and the Amsterdam School architects.",
 story="The Peace Palace houses the Permanent Court of Arbitration set up at the Hague Peace Conference of 1899; the second conference was held in 1907, and a third was planned for 1915.",
 literature="Couperus’s Old People and the Things that Pass (1906).",
 art="Mondrian, in Paris from 1912, moves from trees to abstract grids; Jan Toorop’s symbolist works.",
 ideas="The ‘schools struggle’ over state funding of religious schools, settled in 1917.",
 philosophy="Heymans in Groningen; Hugo de Vries’s mutation theory.",
 science="Lorentz (Nobel 1902) supplies the transformations used in relativity; Kamerlingh Onnes liquefies helium (1908).")
W["BEL"] = dict(
 summary="Coal, steel and textiles make Belgium one of the world’s most industrialised countries.",
 conflicts="Liège’s forts hold out until 16 August; Brussels falls on 20 August; the army withdraws to Antwerp and then the Yser.",
 leaders="Queen Elisabeth; Cardinal Désiré-Joseph Mercier.",
 culture="Antwerp and Ghent are centres of the Flemish movement; Brussels is French-speaking.",
 story="German troops shoot hundreds of civilians in Dinant, Andenne and Leuven during the advance; the burning of the university library and its manuscripts turns world opinion against Germany.",
 literature="Émile Verhaeren’s poems of the industrial city; Maeterlinck’s The Blue Bird (1908).",
 art="Horta’s Hôtel Tassel (1893) is the first Art Nouveau house; Ensor’s masks; Fernand Khnopff.",
 ideas="Universal male suffrage with plural votes (1893); the Congo taken over from Leopold II (1908).",
 philosophy="Cardinal Mercier’s neo-Thomism at Leuven.",
 science="Ernest Solvay funds the first Solvay physics conference in Brussels (1911), with Einstein, Planck and Curie.")
W["DEU"] = dict(
 culture="Berlin is a city of two million, electric trams and department stores; the Social Democrats win the largest share of seats in the 1912 Reichstag election.")
W["AUT"] = dict(
 culture="Vienna’s coffee houses gather Freud, Klimt, Kraus, Schoenberg, Wittgenstein and Trotsky.")
W["HUN"] = dict(
 summary="Hungary has its own parliament, government and army (Honvéd) and shares foreign policy, war and finance with Austria.",
 conflicts="The 1912 ‘Bloody Thursday’ demonstrations for universal suffrage in Budapest.",
 leaders="Count Mihály Károlyi, leader of the opposition.",
 culture="Budapest, united in 1873, grows to nearly 900,000 people; Béla Bartók and Zoltán Kodály collect folk songs.",
 story="Tisza, who has crushed parliamentary obstruction by force in 1912, is the strongest politician in the monarchy; his consent decides that the ultimatum will be sent.",
 literature="Ady’s New Poems (1906) shocks with its symbolism; Mihály Babits and Dezső Kosztolányi write for Nyugat.",
 art="Ödön Lechner’s Hungarian Art Nouveau (Museum of Applied Arts); the painters of Nagybánya.",
 ideas="Liberal nationalism that limits the vote to protect Magyar dominance.",
 philosophy="Georg Lukács and Karl Mannheim in the Sunday Circle.",
 science="Loránd Eötvös’s torsion balance measures gravity with precision.")
W["CZE"] = dict(
 summary="Bohemia and Moravia produce much of the monarchy’s coal, sugar, glass and machinery.",
 conflicts="In 1913 Vienna suspends the Bohemian Diet.",
 leaders="Count Franz Thun, governor of Bohemia.",
 culture="The Sokol gymnastic movement; Czech and German theatres in Prague.",
 story="Kafka, a German-speaking Jewish insurance official, writes The Trial in Prague in the autumn of 1914; Hašek, who will create the good soldier Švejk, is a bohemian journalist.",
 literature="Otokar Březina’s symbolist verse; Rilke and Werfel, Prague-born German poets.",
 art="Czech cubist architecture (Josef Gočár’s House of the Black Madonna, 1912); Kupka in Paris.",
 ideas="Masaryk’s ‘realism’: Czech national rights through democracy and truth in history.",
 philosophy="Masaryk, professor in Prague, exposed the forged ‘medieval’ manuscripts in the 1880s.",
 science="Škoda builds the monarchy’s heavy guns, including the 30.5 cm mortar.")
W["BIH"] = dict(
 summary="A Habsburg governor rules a province where Muslims, Orthodox Serbs and Catholic Croats each form a large part of the population.",
 conflicts="Bogdan Žerajić tries to kill Governor Varešanin in 1910.",
 leaders="Danilo Ilić; Nedeljko Čabrinović (Young Bosnia).",
 culture="Sarajevo’s Baščaršija bazaar and Gazi Husrev-beg Mosque stand beside the Habsburg town hall (1896) and cathedral.",
 story="Princip is one of six assassins armed in Belgrade with the help of officers of the Black Hand; Čabrinović’s bomb misses, but the archduke’s driver later turns into Franz Joseph Street and stops.",
 literature="Petar Kočić’s stories of Bosnian peasants.",
 art="Habsburg architects build Sarajevo’s city hall (Vijećnica) in a pseudo-Moorish style.",
 ideas="Young Bosnia’s students read anarchist and nationalist writers.",
 philosophy="Revolutionary nationalism among high-school students.",
 science="The Habsburgs build narrow-gauge railways, mines and forestry works.")
W["POL"] = dict(
 summary="Warsaw and Łódź are industrial cities of the Russian Empire; Kraków and Lwów have Polish universities and a Polish-run provincial government.",
 conflicts="Russian schools strike (1905); the Prussian school strike in Września (1901–02) against German religious teaching.",
 leaders="Wojciech Korfanty (Polish deputy in the Reichstag).",
 culture="Polish theatres, newspapers and the Catholic church keep a common culture across three borders.",
 story="Piłsudski hopes to raise Russian Poland against the tsar; his riflemen get a cool welcome in Kielce. His Legions fight for Austria, while Dmowski’s National Democrats back Russia.",
 literature="Stefan Żeromski’s novels; Wyspiański’s The Wedding (1901).",
 art="Jacek Malczewski’s symbolism; the Kraków Academy of Fine Arts.",
 ideas="Piłsudski’s armed struggle against Russia versus Dmowski’s national democracy.",
 philosophy="Positivism and Young Poland modernism; Kazimierz Twardowski’s Lwów school of logic.",
 science="Skłodowska-Curie, born in Warsaw, wins Nobel Prizes in physics (1903) and chemistry (1911).")
W["RUS"] = dict(
 culture="Moscow merchants Shchukin and Morozov collect Matisse and Picasso.")
W["FIN"] = dict(
 summary="Finland has its own currency, post, customs and Senate; Russian laws imposed after 1908 limit its parliament.",
 conflicts="The ‘second period of oppression’ from 1908; the 1910 law gives the Russian Duma power over Finnish affairs.",
 leaders="Pehr Evind Svinhufvud, former Speaker, exiled to Siberia in 1914.",
 culture="National Romantic architecture (Helsinki’s National Museum, Tampere Cathedral); choirs, Sibelius’s symphonies and the Kalevala.",
 story="The 1906 Parliament Act replaces the four-estate Diet with a single chamber of 200 members elected by all adults. In the March 1907 election 19 women are elected, the first women members of a national parliament anywhere; nine of them are Social Democrats.",
 literature="Leino’s Whitsongs (1903); Juhani Aho.",
 art="Eliel Saarinen designs Helsinki railway station (competition 1904); Gallen-Kallela’s Kalevala paintings.",
 ideas="Legalists, ‘compliants’ and activists differ on resisting Russification.",
 philosophy="Edvard Westermarck’s sociology of morals.",
 science="The Helsinki University of Technology (1908).")
W["UKR"] = dict(
 summary="Kyiv, Kharkiv and Odesa are Russian imperial cities; Lviv and Chernivtsi are Austrian provincial capitals.",
 conflicts="The Russian army takes Lviv on 3 September 1914; Hrushevsky, returning to Kyiv, is arrested that autumn and exiled to Simbirsk.",
 leaders="Andrey Sheptytsky, Greek Catholic Metropolitan of Lviv.",
 culture="Prosvita reading societies, cooperatives and Ukrainian newspapers spread in Galicia; in Russia Ukrainian is limited in print until 1905.",
 story="In January 1914 the Russian Minister of the Interior bans public commemoration of the centenary of Taras Shevchenko’s birth; students in Kyiv demonstrate anyway and are dispersed by police.",
 literature="Franko’s Moses (1905); Mykhailo Kotsiubynsky’s Shadows of Forgotten Ancestors (1911).",
 art="Mykola Lysenko’s operas; Lviv’s Grand Theatre (1900).",
 ideas="Federalism within Russia, autonomy within Austria, or independence.",
 philosophy="Hrushevsky’s ten-volume History of Ukraine-Rus’ (from 1898) gives Ukraine its own national history.",
 science="The Shevchenko Scientific Society in Lviv acts as a Ukrainian academy of sciences.")
W["SWE"] = dict(
 conflicts="The 1909 general strike.",
 culture="Stockholm hosts the 1912 Olympic Games.",
 literature="Hjalmar Söderberg; Verner von Heidenstam (Nobel 1916).",
 art="Larsson’s watercolours of his family home at Sundborn; Ragnar Östberg’s City Hall (begun 1911).")
W["NOR"] = dict(
 summary="Norway’s merchant fleet is among the largest in the world.",
 conflicts="Norway declares neutrality with Sweden on 8 August 1914.",
 culture="Norway celebrates the centenary of its 1814 constitution with a jubilee exhibition in Kristiania.",
 story="Amundsen’s party of five, with sledge dogs, beats Robert Falcon Scott’s British expedition by five weeks; Scott finds Amundsen’s tent at the pole in January 1912 and dies on the return.",
 literature="Hamsun’s Hunger (1890) and Growth of the Soil (1917); Undset’s Jenny (1911).",
 art="Munch wins the competition for the University Aula, painting The Sun (1911).",
 ideas="Norway gives women the national vote in 1913, after Finland (1906).",
 philosophy="Ivar Aasen’s Landsmål as a nation’s own written language.",
 science="Birkeland’s aurora expeditions; Fridtjof Nansen’s oceanography.")
W["DNK"] = dict(
 summary="Iceland has home rule (1904) and the Danish West Indies are still Danish.",
 conflicts="Denmark mines its waters at German request in August 1914.",
 leaders="Edvard Brandes; the Radical Left (Det Radikale Venstre).",
 culture="Edvard Eriksen’s Little Mermaid is unveiled on the Langelinie in Copenhagen in 1913.",
 story="Bohr’s three-part paper of 1913 combines Rutherford’s nuclear atom with Planck’s quantum, explaining the spectral lines of hydrogen.",
 literature="Pontoppidan’s Lucky Per (1898–1904); Karen Blixen leaves for Kenya in 1913.",
 art="Hammershøi’s grey rooms in Strandgade.",
 ideas="Cooperative movement among farmers.",
 philosophy="Høffding’s philosophy of religion.",
 science="Bohr (Nobel 1922); the Carlsberg Laboratory.")
W["CHE"] = dict(
 summary="Switzerland’s federal army mobilises about 220,000 men in August 1914.",
 conflicts="The ‘trench’ between German- and French-speaking Swiss over the war.",
 leaders="Federal President Arthur Hoffmann (1914).",
 culture="The 1914 National Exhibition in Bern.",
 story="Einstein becomes a professor in Zurich and Prague and returns to Zurich’s ETH in 1912 before leaving for Berlin in 1914.",
 literature="Spitteler, Nobel 1919.",
 art="Hodler’s The Woodcutter (1910) and his history paintings.",
 ideas="The 1874 constitution introduced referendums; the popular initiative followed in 1891.",
 philosophy="Saussure’s course in general linguistics, published by his students in 1916.",
 science="Einstein’s Bern years produce special relativity and the light-quantum (1905).")
W["ITA"] = dict(
 conflicts="Italy annexes Libya and the Dodecanese in the war of 1911–12 against the Ottomans.",
 leaders="Benito Mussolini, editor of Avanti!, expelled from the Socialist Party in November 1914 for supporting war.",
 culture="Giolitti’s 1912 reform extends the vote to almost all adult men.",
 story="The Futurists hold violent ‘serate’ evenings in theatres and campaign for war in 1914–15.",
 literature="Pirandello’s The Late Mattia Pascal (1904).",
 art="Boccioni’s Unique Forms of Continuity in Space (1913).",
 ideas="Italian nationalism (Enrico Corradini’s Nationalist Association, 1910).",
 philosophy="Croce’s journal La Critica.",
 science="Marconi’s wireless telegraphy; Maria Montessori’s method of teaching (1907).")
W["SRB"] = dict(
 summary="Serbia has fought two wars in two years and is exhausted when the ultimatum arrives.",
 conflicts="Austria-Hungary shells Belgrade from across the Danube on 29 July 1914; Kolubara (November–December 1914) drives the invaders out.",
 leaders="Field Marshal Radomir Putnik; Colonel Dragutin Dimitrijević ‘Apis’.",
 culture="Belgrade University (1905) and the National Theatre.",
 story="General Stepa Stepanović’s Second Army defeats Potiorek’s forces at Cer mountain in mid-August, the first Allied victory of the war.",
 literature="Jovan Dučić and Milan Rakić’s verse; Skerlić’s history of Serbian literature.",
 art="Petrović paints expressionist landscapes and works as a nurse in the Balkan Wars.",
 ideas="Yugoslavism among Croat and Slovene students.",
 philosophy="Liberal-radical constitutionalism after 1903.",
 science="Belgrade University (1905); Mihailo Petrović Alas’s mathematics.")
W["GRC"] = dict(
 summary="Greece’s 1911 constitution follows the reforms of Venizelos, who came to power after the Goudi coup of 1909.",
 conflicts="King George I is assassinated in Thessaloniki in March 1913.",
 leaders="Ioannis Metaxas, of the general staff.",
 culture="Athens and Thessaloniki; refugees from Thrace and Asia Minor in 1914.",
 story="The Ottoman garrison of Thessaloniki surrenders to the Greek army on 26 October 1912 (Old Style), a day before Bulgarian troops arrive.",
 literature="Palamas’s The Twelve Lays of the Gypsy (1907); Cavafy’s Ithaka (1911).",
 art="The National Archaeological Museum and the Athens Academy.",
 ideas="Venizelism versus royalism.",
 philosophy="The demotic-versus-katharevousa language question.",
 science="University of Athens.")
W["BGR"] = dict(
 summary="Ferdinand, a German prince, proclaims himself tsar at Tarnovo on 5 October 1908.",
 conflicts="The Bulgarian army takes Adrianople (Edirne) in March 1913 but loses it to the Ottomans in July.",
 leaders="Prime Minister Ivan Geshov (1911–13); Aleksandar Stamboliyski, agrarian leader.",
 culture="Sofia’s National Theatre (1906) and university.",
 story="The Treaty of Bucharest (August 1913) leaves Bulgaria only a strip of Macedonia and Western Thrace on the Aegean; southern Dobruja goes to Romania.",
 literature="Yavorov’s poems; Elin Pelin’s stories.",
 art="Ivan Mrkvička’s paintings of Bulgarian life.",
 ideas="Bulgarian national unification in Macedonia.",
 philosophy="Agrarian and liberal politics.",
 science="Sofia University (1888).")
W["ROU"] = dict(
 summary="Romania’s oil fields are among the largest in Europe.",
 conflicts="In 1913 Romania takes southern Dobruja from Bulgaria.",
 leaders="Queen Elisabeth (Carmen Sylva).",
 culture="Bucharest calls itself ‘Little Paris’; the 1907 peasant revolt was put down by the army with heavy loss of life.",
 story="Romania stays neutral; Brătianu waits to see which side will give Transylvania and Bukovina.",
 literature="George Coșbuc and Octavian Goga, a Transylvanian poet.",
 art="Nicolae Grigorescu’s peasant scenes; Brâncuși’s Bird in Space series begins with Măiastra (1910–12).",
 ideas="Union of all Romanians.",
 philosophy="Junimea circle (Titu Maiorescu).",
 science="Victor Babeș’s bacteriology.")
W["ALB"] = dict(
 summary="The great powers set Albania’s borders at the London Conference (1913) and choose its prince.",
 conflicts="Serbian, Montenegrin and Greek troops occupy parts of Albania in 1912–14; an autonomous Northern Epirus is proclaimed in 1914.",
 leaders="Essad Pasha Toptani.",
 culture="Shkodër Catholic schools and the Marubi studio; Korçë Orthodox schools.",
 story="Qemali raises the flag of Skanderbeg at Vlorë on 28 November 1912 and proclaims independence.",
 literature="Faik Konica’s journal Albania (Brussels, from 1897).",
 art="Marubi photography studio, Shkodër.",
 ideas="Albanian nationalism.",
 philosophy="Sami Frashëri’s programme for an Albanian state.",
 science="The first Albanian schools; the 1908 alphabet.")
W["TUR"] = dict(
 summary="Istanbul has trams, newspapers and political parties after the Young Turk revolution of 1908 restored the constitution.",
 conflicts="The 1908 revolution and the 1909 counter-coup.",
 leaders="Said Halim Pasha, grand vizier.",
 culture="Istanbul’s Pera district.",
 story="Germany’s Goeben and Breslau reach Istanbul on 10 August 1914 and are ‘sold’ to the Ottoman navy, keeping their German crews.",
 literature="Halide Edib’s novels.",
 art="Vedat Tek’s Central Post Office in Istanbul.",
 ideas="The Committee of Union and Progress’s Turkish nationalism.",
 philosophy="Gökalp’s Turkism.",
 science="The Darülfünun (Istanbul University).")
W["MNE"] = dict(
 summary="Montenegro has a constitution (1905) and Russian and Italian subsidies.",
 conflicts="Montenegro is the first to declare war on the Ottomans (8 October 1912).",
 leaders="Crown Prince Danilo.",
 culture="Cetinje’s foreign legations.",
 story="The king’s daughters marry into the royal houses of Italy and Serbia.",
 literature="Njegoš.",
 art="Cetinje’s royal palace and legations.",
 ideas="Union with Serbia versus the Petrović dynasty.",
 philosophy="Njegoš.",
 science="Cetinje’s gymnasium and printing press.")

# ---------------------------------------------------------------- galleries
# Full replacement galleries; anything not listed keeps its base gallery.
IE, IW = IMAGES["enlightenment"], IMAGES["eve-of-war"]
IE["IRL"] = [("Jonathan Swift by Charles Jervas detail.jpg", "Jonathan Swift — Charles Jervas", "literature"),
 ("John Smibert - Bishop George Berkeley - Google Art Project.jpg", "George Berkeley — John Smibert", "philosophy"),
 ("Parliament House, Dublin.jpg", "Parliament House, College Green (1729–39)", "art"),
 ("Portrait of Turlough O'Carolan .PNG", "Turlough O’Carolan, harper (d. 1738)", "culture"),
 ("Trinity College Dublin Front Square.jpg", "Trinity College Dublin, Front Square", "culture")]
IE["ESP"] = [("Ferdinand VI of Spain.jpg", "Ferdinand VI", "leader"),
 ("Zenon de Somodevilla y Bengoechea, Marquis de Ensenada (ca. 1750) - Jacopo Amigoni (Museo El Prado).jpg", "The Marqués de la Ensenada — Jacopo Amigoni, c. 1750", "ideas"),
 ("Jacopo amigoni, il cantante farinelli con amici, 1750-52 circa.JPG", "Farinelli and friends — Jacopo Amigoni, c. 1750–52", "story"),
 ("Royal Palace of Madrid 03.jpg", "Royal Palace of Madrid (from 1738)", "art")]
IE["PRT"] = [("D. João V de Portugal, 1729.jpg", "John V, 1729", "leader"),
 ("Marques de Pombal.jpg", "The Marquis of Pombal", "ideas"),
 ("Mafra May 2013-2.jpg", "Palace-convent of Mafra", "art"),
 ("1755 Lisbon earthquake.jpg", "The Lisbon earthquake of 1755 (contemporary engraving)", "story")]
IE["NLD"] = [("Portret van Willem IV, prins van Oranje-Nassau, RP-P-OB-106.222.jpg", "William IV of Orange, stadtholder 1747–51", "leader"),
 ("Pieter van Musschenbroek. Line engraving by J. Houbraken, 17 Wellcome V0004193.jpg", "Pieter van Musschenbroek — Houbraken", "science"),
 ("Den Haag - Mauritshuis - Cornelis Troost (1696-1750) - 'Nemo loquebatur' (Nobody was speaking) 1740.jpg", "Cornelis Troost, ‘Nemo loquebatur’ (1740)", "art"),
 ("Marriage plate, Netherlands, 18th century, Delftware - Cinquantenaire Museum - Brussels, Belgium - DSC08544.jpg", "Delftware marriage plate, 18th century", "culture")]
IE["BEL"] = [("Liotard, studio of - Charles Alexander of Lorraine, pair.png", "Charles Alexander of Lorraine — studio of Liotard", "leader"),
 ("The Battle of Fontenoy, 11th May 1745.png", "The Battle of Fontenoy, 1745", "story"),
 ("Palace of Charles of Lorraine 1.jpg", "Palace of Charles of Lorraine, Brussels (from 1757)", "art"),
 ("Grand Place Brussels.JPG", "Grand Place, Brussels (guildhouses rebuilt after 1695)", "culture")]
IE["AUT"] = [("Kaiserin Maria Theresia (HRR).jpg", "Maria Theresa", "leader"),
 ("Bernardo Bellotto, gen. Canaletto - Das kaiserliche Lustschloß Schönbrunn, Gartenseite - GG 1667 - Kunsthistorisches Museum.jpg", "Schönbrunn, garden side — Bellotto", "art"),
 ("Hohenfriedeberg - Attack of Prussian Infantry - 1745.jpg", "Hohenfriedeberg, 1745 — the Silesian wars (19th-century painting)", "story"),
 ("Joseph II, Holy Roman Emperor.jpg", "Joseph II, heir to the reforms", "ideas")]
IE["CZE"] = [("Kaiserin Maria Theresia (HRR).jpg", "Maria Theresa, crowned Queen of Bohemia in 1743", "leader"),
 ("Praha St. Nicholas Church Dome 01.jpg", "Dome of St Nicholas, Lesser Town, Prague", "art"),
 ("Clementinum baroque library 2.jpg", "Baroque library hall of the Jesuit Clementinum", "philosophy"),
 ("Prokop Diviš – Jan Vilímek – České album (cropped).jpg", "Prokop Diviš (19th-century portrait by Jan Vilímek)", "science")]
IE["HUN"] = [("Maria Theresia als Königin von Ungarn zu Pferde.jpg", "Maria Theresa as Queen of Hungary", "leader"),
 ("Holy Crown of Hungary.jpg", "Holy Crown of Hungary", "ideas"),
 ("Matthias Bel.jpg", "Mátyás Bél", "science"),
 ("Bratislava Castle, 20210727 1004 0250.jpg", "Pressburg (Bratislava) Castle, seat of the 1741 Diet", "story")]
IE["CHE"] = [("Jean-Jacques Rousseau (painted portrait).jpg", "Jean-Jacques Rousseau", "philosophy"),
 ("Porträt des Daniel Bernoulli (cropped).jpg", "Daniel Bernoulli", "science"),
 ("Albrecht von Haller 1736.jpg", "Albrecht von Haller, 1736", "literature"),
 ("Matterhorn from Domhütte - 2.jpg", "The Alps of Haller’s poem", "culture")]
IE["ITA"] = None  # keep base gallery, add Agnesi below
IE["POL"] = [("Louis de Silvestre - Portrait of Augustus III of Poland - Google Art Project.jpg", "Augustus III — Louis de Silvestre", "leader"),
 ("Anonymous Stanisław Konarski.jpg", "Stanisław Konarski", "ideas"),
 ("Zaluski.jpg", "Józef Andrzej Załuski, co-founder of the Załuski Library", "science"),
 ("Bellotto View of Warsaw from Praga-Krakowskie Przedmiescie.jpg", "Warsaw from Praga — Bellotto (1770; Warsaw a generation later)", "art")]
IE["LTU"] = [("Vilnius Cathedral Exterior 2, Vilnius, Lithuania - Diliff.jpg", "Vilnius Cathedral", "culture"),
 ("Gate of Dawn Exterior, Vilnius, Lithuania - Diliff.jpg", "Gate of Dawn, Vilnius", "religion"),
 ("Vilna Gaon portrait.gif", "The Vilna Gaon (traditional portrait)", "philosophy"),
 ("Vilnius University.Observatory.jpg", "Vilnius University observatory (founded 1753)", "science")]
IE["UKR"] = [("Kyrylo Rozumovsky (Portrait, 2half 18th century, unknown author).jpg", "Hetman Kyrylo Rozumovsky", "leader"),
 ("St. Andrew's Church, Kyiv.jpg", "St Andrew’s Church, Kyiv — Rastrelli", "art"),
 ("Bakhchisaray Palace-2009-2.jpg", "Bakhchisaray, seat of the Crimean khans", "culture"),
 ("Bakhchisarai Palace2.jpg", "Khan’s Palace, Bakhchisaray", "story")]
IE["RUS"] = [("Elizabeth of Russia by L.Tocque (1756).jpg", "Empress Elizabeth — Louis Tocqué, 1756", "leader"),
 ("Mikhail Lomonosov (1757).jpg", "Mikhail Lomonosov, 1757", "science"),
 ("Catherine Palace in Tsarskoe Selo.jpg", "Catherine Palace, Tsarskoye Selo — Rastrelli", "art"),
 ("Saint Petersburg Smolny Cathedral IMG 5855 1280.jpg", "Smolny Cathedral, St Petersburg", "religion")]
IE["SWE"] = [("Adolph Frederick of Sweden c 1751 by Gustaf Lundberg & Jakob Björck.jpg", "Adolf Frederick, c. 1751", "leader"),
 ("Carl von Linné.jpg", "Carl Linnaeus — Alexander Roslin", "science"),
 ("Anders Celsius.jpg", "Anders Celsius", "science"),
 ("Stockholm Royal Palace.jpg", "Royal Palace, Stockholm (completed 1754)", "art"),
 ("Drottningholm Palace (by Pudelek) 1.jpg", "Drottningholm Palace", "culture")]
IE["FIN"] = [("Suomenlinna.jpg", "Sveaborg (Suomenlinna), begun 1748", "story"),
 ("Augustin Ehrensvärd x J H Scheffel.jpg", "Augustin Ehrensvärd — J. H. Scheffel", "leader"),
 ("Turku Cathedral Turku.jpg", "Turku Cathedral, seat of Finland’s bishop", "religion"),
 ("PehrKalm.jpg", "Pehr Kalm", "science")]
IE["DNK"] = [("Pilo - Frederik V of Denmark.jpg", "Frederick V — Carl Gustaf Pilo", "leader"),
 ("Adam Gottlob Moltke.jpg", "Adam Gottlob Moltke", "ideas"),
 ("Frederik V statue in Amalienborg Palace Copenhagen 2014 01.jpg", "Amalienborg and Saly’s statue of Frederick V (unveiled 1771)", "art"),
 ("Ludvig Holberg.jpg", "Ludvig Holberg", "literature")]
IE["NOR"] = [("Akershus festning.jpg", "Akershus Fortress, Christiania", "culture"),
 ("Holberg 1757 by Bernigeroth.jpg", "Ludvig Holberg — engraving by Bernigeroth, 1757", "literature"),
 ("Fassaden in Bryggen, Bergen N.jpg", "Bryggen, the merchant wharf of Bergen (rebuilt after 1702)", "story"),
 ("Rosemaling.jpg", "Rose painting (rosemaling)", "art")]
IE["TUR"] = [("Sultan Mahmud I – Jean Baptiste Vanmour.jpg", "Mahmud I — Jean-Baptiste Vanmour", "leader"),
 ("Nuruosmaniye Mosque Mars 2013.jpg", "Nuruosmaniye Mosque (1748–55)", "art"),
 ("Fountain of Ahmed III Topkapi.jpg", "Fountain of Ahmed III, Topkapı", "culture"),
 ("Map of the Indian Ocean and the China Sea was engraved in 1728 by Ibrahim Müteferrika.jpg", "Map printed by İbrahim Müteferrika, 1728", "science")]
IE["GRC"] = [("Eugenios Voulgaris.jpg", "Eugenios Voulgaris", "philosophy"),
 ("Monastery of Vatopedi & Athoniada Academia.jpg", "Vatopedi and the site of the Athonite Academy", "story"),
 ("Doric portico in Athens - J. Stuart & N. Revett - 1751.jpg", "Athens drawn by Stuart and Revett, 1751", "art"),
 ("Parthenon.jpg", "The Parthenon, damaged in 1687, under Ottoman rule", "culture")]
IE["ROU"] = [("Constantin Mavrocordat.jpg", "Constantine Mavrocordatos", "leader"),
 ("Ioan Inocentiu Micu Klein.jpg", "Bishop Inochentie Micu-Klein", "ideas"),
 ("Horezu Monastery.jpg", "Horezu Monastery, Brâncovenesc style", "art"),
 ("Curtea de Arges monastery.JPG", "Curtea de Argeș Monastery", "religion")]
IE["SRB"] = [("Kalemegdan.jpg", "Belgrade fortress (Kalemegdan), rebuilt by Austria and returned in 1739", "story"),
 ("Arsenije IV Jovanović Šakabenta.jpg", "Patriarch Arsenije IV Jovanović Šakabenta", "leader"),
 ("Krušedol monastery 0035.JPG", "Krušedol Monastery, Fruška Gora", "religion"),
 ("St Nicholas Cathedral in Sremski Karlovci.jpg", "Cathedral of St Nicholas, Sremski Karlovci (1758–62)", "art")]
EXTRA = {"enlightenment": {"ITA": [("Portrait of Maria Gaet - Agnesi MET DP805437.jpg", "Maria Gaetana Agnesi", "science")]},
         "eve-of-war": {}}

IW["GBR"] = None
EXTRA["eve-of-war"]["GBR"] = [("Ernest Rutherford 1908.jpg", "Ernest Rutherford, 1908", "science")]
IW["IRL"] = [("John Redmond, circa 1909.jpg", "John Redmond, c. 1909", "leader"),
 ("Patrick Pearse.jpg", "Patrick Pearse", "ideas"),
 ("James Joyce by Alex Ehrenzweig, 1915 cropped.jpg", "James Joyce, 1915", "literature"),
 ("William Butler Yeats by George Charles Beresford.jpg", "W. B. Yeats — George Charles Beresford, 1911", "culture")]
IW["ESP"] = [("Rey Alfonso XIII de España, by Kaulak (cropped).jpg", "Alfonso XIII — Kaulak", "leader"),
 ("La Sagrada Familia en construcción, c. 1915.jpg", "Sagrada Família under construction, c. 1915", "art"),
 ("Joaquín Sorolla. Santiago Ramón y Cajal 1906.jpg", "Santiago Ramón y Cajal — Sorolla, 1906", "science"),
 ("Antonio Machado Campos de Castilla 1912.jpg", "Antonio Machado’s Campos de Castilla (1912)", "literature")]
IW["PRT"] = [("Fotografia oficial do Presidente da República Manuel de Arriaga. 1912.jpg", "President Manuel de Arriaga, 1912", "leader"),
 ("Auto da Proclamação da República Portuguesa - Estúdio Novais.jpg", "Act of proclamation of the Portuguese Republic, 1910", "story"),
 ("D. Manuel II - Benoliel (Cabral Moncada).png", "Manuel II, the last king — Joshua Benoliel", "culture"),
 ("Amadeo de Souza Cardoso with tie and looking right.jpg", "Amadeo de Souza-Cardoso", "art")]
IW["NLD"] = [("Queen Wilhelmina2.jpg", "Queen Wilhelmina", "leader"),
 ("Friedenspalast Den Haag.jpg", "Peace Palace, The Hague (1913)", "ideas"),
 ("Kamerlingh portret.jpg", "Heike Kamerlingh Onnes", "science"),
 ("Piet mondrian, composizione alberi 2, 1912-13.jpg", "Mondrian, Composition Trees 2 (1912–13)", "art")]
IW["BEL"] = [("Portrait of Albert I of Belgium (cropped).jpg", "Albert I of Belgium", "leader"),
 ("Havoc of War - Ruins - France - Cities - L - RUINS OF THE LIBRARY AT Louvain, destroyed by the Germans in 1914 - NARA - 31484207.jpg", "Ruins of the university library, Leuven, 1914", "story"),
 ("Victor Horta Hotel Tassel.JPG", "Victor Horta’s Hôtel Tassel, Brussels (1893)", "art"),
 ("Grand Place Brussels.JPG", "Grand Place, Brussels", "culture")]
IW["HUN"] = [("Istvan Tisza.jpg", "István Tisza", "leader"),
 ("Budapest Parliament 4604.JPG", "Hungarian Parliament, Budapest (1904)", "art"),
 ("Ady Endre (Székely Aladár felvétele).jpg", "Endre Ady — Aladár Székely", "literature"),
 ("Eötvös Loránd (Székely Aladár felvétele, 1912).jpg", "Loránd Eötvös, 1912", "science")]
IW["CZE"] = [("Tomáš Garrigue Masaryk.jpg", "Tomáš Garrigue Masaryk", "leader"),
 ("Prague Municipal House 01.jpg", "Municipal House, Prague (1912)", "art"),
 ("Alfons Mucha at work on Slav Epic.jpg", "Mucha at work on the Slav Epic", "culture"),
 ("Franz Kafka, passport photograph, 1915–1916.jpg", "Franz Kafka, 1915–16", "literature")]
IW["BIH"] = [("Assassination of Archduke Franz Ferdinand 1914.jpg", "The Sarajevo assassination, 28 June 1914", "story"),
 ("Gavrilo Princip, cell, headshot, bw (cropped).jpg", "Gavrilo Princip", "leader"),
 ("The Latin Bridge, Sarajevo.jpg", "Latin Bridge, Sarajevo", "culture"),
 ("Gazi Husrev-beg's Mosque 01.jpg", "Gazi Husrev-beg Mosque, Sarajevo", "religion")]
IW["POL"] = [("Józef Piłsudski 1914.jpg", "Józef Piłsudski, 1914", "leader"),
 ("Marie Skłodowska-Curie's Nobel Prize in Chemistry 1911.jpg", "Marie Skłodowska-Curie’s Nobel Prize diploma (1911)", "science"),
 ("Bernhard Wahtl, Henryk Sienkiewicz, portret, MHF 48272 F (MuFo).jpg", "Henryk Sienkiewicz — Bernhard Wahtl", "literature"),
 ("Wladyslaw Reymont 1897 (71364799) (cropped).jpg", "Władysław Reymont, 1897", "culture")]
IW["RUS"] = None
EXTRA["eve-of-war"]["RUS"] = [("Winter Palace in 1914 by Yakov Steinberg.jpg", "Winter Palace, 1914 — Yakov Steinberg", "story")]
IW["FIN"] = [("Jean Sibelius, 1913.jpg", "Jean Sibelius, 1913", "culture"),
 ("First Female Parliamentarians in the world in Finland in 1907.jpg", "The first women members of parliament, Finland, 1907", "story"),
 ("Eino Leino 1905c.jpg", "Eino Leino, c. 1905", "literature"),
 ("Adolf Paul painted by Akseli Gallen-Kallela in 1903.jpg", "Gallen-Kallela, portrait of Adolf Paul (1903)", "art")]
IW["UKR"] = [("М. С. Грушевський. 1914 р. Фото з матеріалів Київського ГЖУ.jpg", "Mykhailo Hrushevsky, 1914 (Kyiv gendarmerie file photo)", "leader"),
 ("Ivan Franko 2.jpg", "Ivan Franko", "literature"),
 ("Lesya Ukrainka portrait.jpg", "Lesya Ukrainka", "literature"),
 ("Lviv Theatre of Opera and Ballet 29.07.2008.jpg", "Lviv’s Grand Theatre (1900)", "art"),
 ("Taras Shevchenko - portrait by Ivan Kramskoi.jpg", "Taras Shevchenko, whose 1914 centenary was banned (Kramskoi, 1871)", "culture")]
IW["SWE"] = [("Gustav V speaks in 1914.jpg", "Gustaf V’s Courtyard Speech, 1914", "story"),
 ("Selma Lagerlöf.jpg", "Selma Lagerlöf", "literature"),
 ("August Strindberg.jpg", "August Strindberg", "literature"),
 ("Frukost under stora björken av Carl Larsson 1896.jpg", "Carl Larsson, Breakfast under the Big Birch (1896)", "art")]
IW["NOR"] = [("Haakon VII FSA.jpg", "Haakon VII", "leader"),
 ("Scotts Gruppe am Polheim-Zelt Amundsens.jpg", "Scott’s party at Amundsen’s tent at the South Pole, January 1912", "story"),
 ("Edvard Munch - The Sun (1911).jpg", "Munch, The Sun (1911), for the University Aula", "art"),
 ("Fin Haakon Frølich - Knut Hamsun - Norsk portrettarkiv - Riksantikvaren - H000153.jpg", "Knut Hamsun", "literature")]
IW["DNK"] = [("Christian X of Denmark circa 1915.jpg", "Christian X", "leader"),
 ("Niels Bohr.jpg", "Niels Bohr", "science"),
 ("Vilhelm Hammershøi, Interiør fra Strandgade 30, 1900.jpg", "Hammershøi, Interior, Strandgade 30 (1900)", "art"),
 ("Assembly of the Little Mermaid statue (Copenhagen, Langeline, 1913).jpg", "The Little Mermaid being installed, 1913", "culture")]
IW["CHE"] = [("Einstein special relativity manuscript.jpg", "Einstein’s relativity manuscript", "science"),
 ("Ferdinand Hodler - Woodcutter - Google Art Project.jpg", "Hodler, The Woodcutter (1910)", "art"),
 ("Carl spitteler 1905.jpg", "Carl Spitteler, 1905", "literature"),
 ("Matterhorn from Domhütte - 2.jpg", "The Matterhorn", "culture")]
IW["ITA"] = [("1914-Vittorio-Emanuele-III-Italia.jpg", "Victor Emmanuel III, 1914", "leader"),
 ("Giolitti ritratto.jpg", "Giovanni Giolitti", "ideas"),
 ("Unique Forms of Continuity in Space MET DT6411.jpg", "Boccioni, Unique Forms of Continuity in Space (1913)", "art"),
 ("Guglielmo Marconi 1909.jpg", "Guglielmo Marconi, 1909", "science")]
IW["SRB"] = [("Peter I of Serbia.jpg", "Peter I of Serbia", "leader"),
 ("Nikola Pasic.jpg", "Nikola Pašić", "ideas"),
 ("His Majesty King Petar on the position during the battle of Cer watches development of the battle on the front of the 2nd Army.png", "King Peter watching the Battle of Cer, August 1914", "story"),
 ("After the battle of Cer, captured Austro-Hungarian munition park at Tekeriš (Front Morava Division 1).png", "Captured Austro-Hungarian munitions after Cer, 1914", "culture")]
IW["GRC"] = [("Constantine I of Greece in 1914.jpg", "Constantine I, 1914", "leader"),
 ("Eleftherios Venizelos.jpg", "Eleftherios Venizelos", "ideas"),
 ("Achille Beltrame - Greek army enters Thessaloniki.jpg", "The Greek army enters Thessaloniki, 1912 — Achille Beltrame", "story"),
 ("Konstantinos Kavafis.jpg", "Constantine Cavafy", "literature")]
IW["BGR"] = [("Ferdinand of Bulgaria.jpg", "Tsar Ferdinand", "leader"),
 ("Alexander Nevsky Cathedral, Sofia.jpg", "Alexander Nevsky Cathedral, Sofia", "art"),
 ("BASA-937K-1-410-7-Ivan Vazov (cropped).JPG", "Ivan Vazov", "literature"),
 ("BASA-373K-1-697-9-Peyo Yavorov (cropped, enhanced).jpg", "Peyo Yavorov", "culture")]
IW["ROU"] = [("Carol I of Romania.jpg", "Carol I", "leader"),
 ("Ion I C Bratianu - Foto01.jpg", "Ion I. C. Brătianu", "ideas"),
 ("Romanian Athenaeum.jpg", "Romanian Athenaeum", "culture"),
 ("Castle Peleş in 2009.jpg", "Peleș Castle", "art")]
IW["ALB"] = [("Ismail Qemali.jpg", "Ismail Qemali", "leader"),
 ("Prince Wilhelm of Wied.png", "Prince Wilhelm of Wied", "story"),
 ("Assembly of Vlorë.jpg", "The Assembly of Vlorë, November 1912", "ideas"),
 ("Deklarata e Pavarësisë (dokumenti origjinal 1912).jpg", "The declaration of independence, 1912", "culture")]
IW["TUR"] = None
EXTRA["eve-of-war"]["TUR"] = [("Battlecruiser SMS Goeben transfered to the Ottoman Empire and renamed the Yavuz 1914 (49911053158) (cropped).jpg", "Goeben as the Ottoman Yavuz, 1914", "story")]
IW["MNE"] = [("Nicholas I of Montenegro.jpg", "Nicholas I of Montenegro", "leader"),
 ("King Nicholas of Montenegro (1911).jpg", "King Nicholas, 1911", "culture"),
 ("Cetinje Monastery.jpg", "Cetinje Monastery", "religion"),
 ("Ottoman soldiers displaying the captured standard of the Montenegrin force during the Siege of Scutari.jpg", "Siege of Scutari, 1913: Ottoman defenders with a captured Montenegrin standard", "story")]
for d in (IE, IW):
    for k in [k for k, v in d.items() if v is None]:
        del d[k]

# Stories rewritten (not appended) where the depth text supersedes the original sentence.
for _pid, _iso in (("enlightenment", "NOR"), ("eve-of-war", "FIN"), ("eve-of-war", "UKR")):
    SET[_pid].setdefault(_iso, {})["story"] = ADD[_pid][_iso].pop("story")
SET["enlightenment"]["NOR"]["story"] = ("The Strömstad treaty fixes the long Norwegian–Swedish border. " + SET["enlightenment"]["NOR"]["story"])
SET["eve-of-war"]["UKR"]["story"] = SET["eve-of-war"]["UKR"]["story"]
SET["eve-of-war"]["GRC"] = {"story": "Under the 1913 Treaty of Bucharest Greece keeps Thessaloniki and southern Macedonia; with Epirus and Crete, its territory and population grow by more than half."}

# ---------------------------------------------------------------- second depth pass
def _more(pid, iso, **kw):
    d = ADD[pid].setdefault(iso, {})
    for f, t in kw.items():
        d[f] = (d[f] + " " + t) if f in d else t

_more("enlightenment", "GBR", conflicts="In North America, Fort Duquesne and the Ohio valley spark fighting with France in 1754, two years before war is declared in Europe.", science="The Royal Society awards the Copley Medal to Benjamin Franklin (1753) for his electrical experiments.")
_more("enlightenment", "FRA", conflicts="The Battle of Fontenoy (11 May 1745), won by Marshal de Saxe in the king’s presence, is France’s great victory of the war.", religion="The ‘refusal of sacraments’ to Jansenists sets the Paris Parlement against the archbishop in the 1750s.", ideas="Quesnay’s Tableau économique (1758) founds the physiocrats’ economics.", art="Madame de Pompadour patronises Boucher and the Sèvres porcelain works (moved to Sèvres in 1756).")
_more("enlightenment", "DEU", summary="Saxony, Hanover (in personal union with Britain) and Bavaria are second-rank powers; the prince-bishoprics and imperial cities survive inside the Empire’s courts and Diet at Regensburg.", conflicts="Frederick invades Saxony in August 1756, opening the Seven Years’ War on the continent.", religion="Moses Mendelssohn arrives in Berlin in 1743 and becomes the leading Jewish philosopher of the German Enlightenment.", culture="Leipzig and Frankfurt book fairs make German the language of a growing publishing market.", story="In 1750 Voltaire arrives at Potsdam as Frederick’s guest; the friendship ends in a quarrel and his arrest in Frankfurt in 1753.", ideas="Frederick’s Anti-Machiavel (1740) and his reforms of torture and justice.")
_more("enlightenment", "AUT", conflicts="The Treaty of Aix-la-Chapelle (1748) confirms the Pragmatic Sanction but leaves Silesia with Prussia.", religion="Crypto-Protestants from Upper Austria and Carinthia are deported to Transylvania under the ‘transmigration’ policy.")
_more("enlightenment", "ITA", conflicts="The Treaty of Aranjuez (1752) between Austria, Spain and Sardinia guarantees the Italian settlement for a generation.", culture="Venice’s carnival, opera houses and gaming rooms draw British and German visitors on the Grand Tour.", story="Charles of Bourbon also builds the Teatro di San Carlo in Naples (1737), the Capodimonte palace and porcelain works, and begins the palace of Caserta in 1752 to Luigi Vanvitelli’s designs.", literature="Goldoni writes sixteen new comedies for the 1750–51 season in Venice; Metastasio works at the Vienna court.", ideas="Pietro Verri and Cesare Beccaria in Milan will turn this climate into On Crimes and Punishments (1764).", philosophy="Antonio Genovesi takes the first European chair of political economy in Naples (1754).", science="Bassi, the first woman to hold a university chair in physics, teaches Newtonian experimental physics in Bologna.")
_more("enlightenment", "RUS", religion="Elizabeth expels Jews from the empire (1742) and favours the Orthodox establishment.", literature="Vasily Trediakovsky reforms Russian versification.")
_more("enlightenment", "DNK", religion="Hans Egede’s Lutheran mission in Greenland (from 1721) brings the Inuit under Danish rule.")
_more("enlightenment", "NOR", culture="The Norwegian timber trade with Britain and the Netherlands makes Christiania’s merchant families, such as the Ankers, rich.", religion="Pietist revival reaches Norwegian parishes; confirmation becomes compulsory in 1736.")
_more("enlightenment", "TUR", leaders="Grand viziers such as Koca Ragıp Pasha (1757–63), a poet and reformer.", religion="The Ecumenical Patriarchate in the Phanar heads all Orthodox Christians of the empire.")
_more("enlightenment", "GRC", leaders="Venetian proveditors in Corfu.")

W2 = lambda iso, **kw: _more("eve-of-war", iso, **kw)
W2("GBR", conflicts="The Agadir crisis (1911) and the Anglo-German naval race, in which Britain launches HMS Dreadnought in 1906.", religion="Welsh disestablishment passes in 1914 and is suspended for the war.", literature="H. G. Wells and Arnold Bennett write of the new lower-middle class; Rupert Brooke’s war sonnets follow in 1914.", art="Roger Fry’s Omega Workshops (1913); Wyndham Lewis’s Blast (1914).", ideas="The Labour Party, founded 1900, holds 42 seats after December 1910.", philosophy="G. E. Moore’s Principia Ethica (1903) shapes the Bloomsbury group.")
W2("IRL", religion="The Catholic Church controls most schools; the Ne Temere decree (1908) on mixed marriages alarms Protestants.", leaders="Arthur Griffith (Sinn Féin).")
W2("FRA", summary="Its colonial empire stretches from North and West Africa to Indochina; Morocco becomes a French protectorate in 1912.", conflicts="The Battle of the Frontiers (August 1914) costs France some 27,000 dead in a single day, 22 August; the Marne halts the German armies in September.", religion="The Dreyfus affair (1894–1906) splits the country between Catholic nationalists and republicans.", culture="The Tour de France (1903), the Pathé and Gaumont film studios and the department store.", story="Jaurès, the socialist leader who has campaigned against war, is shot in a Paris café on 31 July; on 4 August his opponents and supporters together vote war credits in the ‘Sacred Union’.", literature="Charles Péguy, killed at the Marne in September 1914.", art="The Salon d’Automne and the Section d’Or; Robert and Sonia Delaunay’s Orphism.", ideas="The 1913 Three-Year Law extends military service to three years.", philosophy="Bergson’s lectures at the Collège de France attract crowds.", science="Henri Poincaré (d. 1912); Louis Blériot crosses the Channel by air on 25 July 1909.")
W2("ESP", religion="The ‘Padlock Law’ (1910) limits new religious orders.")
W2("PRT", religion="The 1911 Law of Separation seizes church property.")
W2("NLD", religion="Abraham Kuyper’s Anti-Revolutionary Party and the Catholic party govern together in 1901–05 and 1908–13.", leaders="Hendrikus Colijn, Minister of War (1911–13).")
W2("BEL", religion="Catholic governments have ruled since 1884.", culture="The Brussels World’s Fair of 1910 and the Ghent exposition of 1913.")
W2("DEU", summary="The Reichstag, elected by universal male suffrage, votes the budget but cannot dismiss the chancellor.", conflicts="The Zabern affair (1913) in Alsace shows the army’s contempt for civilian authority.", religion="Bismarck’s Kulturkampf against the Catholic Church (1870s) has left the Centre Party strong.", story="Moltke’s plan sends seven armies through Belgium and Luxembourg to envelop France in six weeks, leaving one to hold East Prussia; the Russian invasion of East Prussia is destroyed at Tannenberg (26–30 August).", literature="Gerhart Hauptmann (Nobel 1912); Heinrich Mann.", art="Peter Behrens designs AEG factories and products; Walter Gropius’s Fagus Works (1911–13); the Werkbund exhibition in Cologne (1914).", ideas="Pan-German League and Navy League agitation.", philosophy="Neo-Kantianism at Marburg (Hermann Cohen) and the Heidelberg sociologists.", science="Fritz Haber and Carl Bosch make ammonia from air (1909–13); Wilhelm Röntgen’s X-rays (1895).")
W2("AUT", summary="The Austrian half (Cisleithania) has a parliament elected by universal male suffrage since 1907, paralysed by quarrels between nationalities.", conflicts="The Austro-Hungarian armies are beaten by Serbia at Cer and by Russia in Galicia, losing Lemberg (Lviv) in September 1914.", religion="Karl Lueger, Christian Social mayor of Vienna (1897–1910), mixes Catholic politics with antisemitism.", story="Conrad von Hötzendorf has urged war on Serbia again and again since 1906; after Sarajevo the old emperor agrees, with Germany’s promise of support.", literature="Stefan Zweig; Robert Musil’s Young Törless (1906); Georg Trakl, who dies in Kraków in November 1914.", art="Otto Wagner’s Postal Savings Bank (1906); the Wiener Werkstätte; Kokoschka’s The Bride of the Wind (1913–14).", ideas="Austro-Marxists Karl Renner and Otto Bauer propose cultural autonomy for nationalities.", philosophy="Ernst Mach’s empiricism; Ludwig von Mises and the Austrian school of economics.", science="Karl Landsteiner discovers blood groups (1901); Victor Hess discovers cosmic rays in balloon flights (1912).")
W2("HUN", religion="Hungarian Jews are prominent in Budapest’s professions, press and industry.")
W2("CZE", religion="The Hussite memory is celebrated in the Jan Hus monument (1915), planned for the 500th anniversary of his death.", leaders="Josef Scheiner, head of the Sokol.")
W2("BIH", leaders="Franz Ferdinand’s wife Sophie, Duchess of Hohenberg, killed beside him.")
W2("POL", religion="The Catholic Church and Jewish communities of Warsaw, Łódź and Kraków; the Bund and Zionists organise among Jews.")
W2("RUS", summary="Its population of about 170 million makes it the largest state in Europe; Pyotr Stolypin’s land reforms (1906–11) create a class of peasant proprietors before his assassination in 1911.", conflicts="Strikes in St Petersburg reach a peak in July 1914; the Second Army is destroyed at Tannenberg, but Russia conquers Austrian Galicia.", leaders="Grand Duke Nicholas, commander-in-chief; Grigory Rasputin at court.", religion="Pogroms (Kishinev 1903; 1905) and the Beilis trial (1913) show official antisemitism.", culture="The World of Art (Mir iskusstva) circle, the Moscow Art Theatre of Stanislavsky and Chekhov, and the first Russian cinemas.", story="Sazonov persuades the tsar to order general mobilisation on 30 July; Germany demands it be stopped and declares war on 1 August. Crowds kneel before the Winter Palace as Nicholas II swears not to make peace while an enemy remains on Russian soil.", literature="Maxim Gorky; Anna Akhmatova’s Evening (1912) and Rosary (1914); the Futurists’ A Slap in the Face of Public Taste (1912).", art="Malevich’s first Suprematist works follow in 1915; Natalia Goncharova and Mikhail Larionov’s Rayonism.", ideas="Lenin’s Bolsheviks and the Mensheviks split the Social Democrats (1903); the Kadets lead the liberals.", philosophy="The Vekhi (Landmarks) symposium of 1909 attacks the radical intelligentsia.", science="Pavlov’s conditioned reflexes; Konstantin Tsiolkovsky’s rocket equation (1903); Igor Sikorsky’s four-engined Ilya Muromets airliner (1913).")
W2("FIN", religion="Lutheran church and the revivalist movements of Ostrobothnia.", art="Akseli Gallen-Kallela’s Kalevala frescoes in the National Museum.")
W2("UKR", religion="Metropolitan Sheptytsky is arrested by the Russian army in Lviv in September 1914 and deported to Russia.")
W2("SWE", summary="Sweden has grown rich from iron ore, timber and engineering firms such as ASEA, SKF and Ericsson.", religion="Free churches and the temperance movement are powerful popular movements.", story="Sweden declares neutrality in August 1914 and, with Norway and Denmark, the three kings meet at Malmö in December to affirm it.", ideas="The Social Democrats, led by Hjalmar Branting, become the largest party in the Second Chamber in 1914.", philosophy="Axel Hägerström’s Uppsala school.", science="Arrhenius (Nobel 1903) explains how carbon dioxide warms the climate (1896); Gustaf Dalén (Nobel 1912) for lighthouse technology.")
W2("NOR", religion="The Lutheran state church and lay movements inspired by Hans Nielsen Hauge.")
W2("DNK", religion="Grundtvigian folk high schools.", story="Christian X declares neutrality in August 1914.")
W2("CHE", religion="Calvinist Geneva and Catholic central Switzerland; the Kulturkampf has ended.", story="Switzerland becomes the home of the International Committee of the Red Cross’s prisoner-of-war agency (opened in Geneva in August 1914).")
W2("ITA", religion="Pope Pius X dies on 20 August 1914; Benedict XV succeeds.", story="Italy refuses to follow its allies in August 1914, because Austria-Hungary attacked Serbia without consulting it; Salandra’s ‘sacred egoism’ bargains with both sides.")
W2("SRB", religion="The Serbian Orthodox Church becomes the church of Kosovo and Macedonia after 1912.")
W2("GRC", religion="The Ecumenical Patriarch stays in Constantinople; the Church of Greece is autocephalous.", ideas="Venizelos favours the Entente; Constantine, the Kaiser’s brother-in-law, favours neutrality.")
W2("BGR", religion="The Bulgarian Exarchate, created by the sultan in 1870, competes with Greek and Serbian churches in Macedonia.", ideas="Ferdinand moves towards Germany after 1913.")
W2("ROU", religion="Romanian Orthodox Church autocephalous since 1885.", ideas="The Cultural League campaigns for Transylvanian Romanians.")
W2("ALB", religion="Bektashi Sufis, Sunni Muslims, Orthodox and Catholics share one nation.", ideas="The Congress of Manastir (1908) chooses the Latin alphabet.")
W2("TUR", religion="Caliph Mehmed V proclaims jihad against the Entente in November 1914.", culture="The Balkan refugees settle in Istanbul and Anatolia.")
W2("MNE", conflicts="Montenegro’s army joins Serbia in the 1914 campaign in Bosnia.", leaders="Prime Minister Janko Vukotić.", religion="Cetinje Monastery, seat of the metropolitan.", culture="Cetinje, a town of a few thousand people, has a theatre (Zetski Dom, 1896) and foreign legations.", story="King Nicholas has ruled since 1860; his court is famous for marrying daughters into European royalty, including Elena, Queen of Italy.", art="Cetinje’s court and government buildings.", ideas="Nicholas I’s autocracy versus the Club party.", philosophy="Njegoš’s The Mountain Wreath as a national epic.", science="The Cetinje printing press, successor of the fifteenth-century Crnojević press.")
# the MNE first-pass story duplicated by the line above
ADD["eve-of-war"]["MNE"]["story"] = ADD["eve-of-war"]["MNE"]["story"].replace("The king’s daughters marry into the royal houses of Italy and Serbia. ", "")
W2("ROU", leaders="Take Ionescu, Conservative-Democrat leader.", literature="Ion Luca Caragiale (d. 1912), master of comedy; Liviu Rebreanu’s first stories.", art="Ștefan Luchian (d. 1916).", science="Coandă’s experimental ducted aircraft shown in Paris in 1910.")
W2("DNK", leaders="Thorvald Stauning, Social Democratic leader.", literature="Martin Andersen Nexø’s Pelle the Conqueror (1906–10).", art="Carl Nielsen’s Fourth Symphony (‘The Inextinguishable’) begun in 1914.", ideas="The Radicals’ government of 1913 prepares women’s suffrage.")
W2("ALB", leaders="Prenk Bib Doda; Isa Boletini, northern rebel leader.", culture="Albanian clubs and newspapers in Bucharest, Sofia, Istanbul and Boston.", literature="Ndre Mjeda and Gjergj Fishta, Catholic poets of Shkodër.")
W2("BGR", leaders="Nikola Genadiev; Vasil Kolarov, socialist leader.", culture="Plovdiv’s tobacco trade and the Thracian refugees of 1913.", literature="Aleko Konstantinov’s Bay Ganyo (1895).")
W2("FIN", conflicts="Russia keeps a large garrison and fortifies the coast in 1914; Finns are exempt from conscription.", ideas="Activist students start secret contacts with Germany late in 1914 (the Jäger movement).")
W2("MNE", literature="King Nicholas himself writes poetry and plays, including The Empress of the Balkans (1884).")
W2("NOR", leaders="Christian Michelsen, prime minister at independence in 1905.", literature="Olav Duun and Johan Bojer; Henrik Ibsen (d. 1906).", art="Gustav Vigeland works on the great fountain commissioned by Kristiania in 1906.", philosophy="Nansen’s humanitarian internationalism.")
W2("SWE", leaders="Karl Staaff, Liberal prime minister until February 1914.", culture="The 1909 strike and the cooperative movement.", literature="Pär Lagerkvist’s expressionist Word Art and Picture Art (1913).")
W2("CHE", leaders="Gustave Ador, president of the ICRC.", culture="Dada will be born in Zurich’s Cabaret Voltaire in 1916 among wartime exiles.", literature="Robert Walser’s Jakob von Gunten (1909); Charles-Ferdinand Ramuz.", ideas="Neutrality guaranteed by the great powers in 1815.")
W2("ITA", religion="The ‘non expedit’ forbidding Catholics to vote is relaxed by the Gentiloni pact (1913).", culture="FIAT (1899), Pirelli and Olivetti (1908) lead northern industry.", philosophy="Vilfredo Pareto’s theory of elites.")
W2("GRC", leaders="Prime Minister Venizelos’s Liberal Party.", culture="The Olympic revival: Athens hosted the first modern Games in 1896.", art="Nikolaos Gyzis (d. 1901) and the Munich school.")
W2("SRB", culture="Belgrade cafés such as the Zlatna Moruna where Young Bosnians gather.", literature="Borisav Stanković’s Impure Blood (1910).")
W2("TUR", leaders="Grand Vizier Said Halim and Kaiser’s envoy Hans von Wangenheim.", literature="Mehmet Akif’s Islamist poetry (Safahat).", art="Osman Hamdi Bey (d. 1910), painter and founder of the Istanbul Archaeology Museum.")
W2("ESP", culture="Barcelona’s Palau de la Música Catalana (1908) and Madrid’s Gran Vía (begun 1910).", art="Gaudí’s Casa Milà (1906–12).")
W2("PRT", culture="Lisbon cafés like A Brasileira (1905) host the modernists.", art="Columbano Bordalo Pinheiro’s portraits.")
W2("NLD", culture="Bicycles, cocoa, Philips light bulbs (1891) and Royal Dutch Shell (1907).", art="Kees van Dongen in Paris.")
W2("BEL", literature="Georges Eekhoud and Stijn Streuvels (in Flemish).", philosophy="Paul Otlet and Henri La Fontaine’s Mundaneum and Universal Decimal Classification.")
W2("HUN", culture="The Budapest metro (1896), the first on the European continent.", art="Bartók’s Bluebeard’s Castle (1911).")
W2("BIH", culture="Habsburg schools, the National Museum (1888) and the Sarajevo Haggadah, rediscovered in 1894.")
W2("POL", culture="The Polish Academy of Learning in Kraków (1872).", art="Józef Mehoffer’s stained glass for Fribourg Cathedral.")
W2("UKR", culture="Odesa, with its port, Jewish life and grain trade, is the fourth city of the Russian Empire.", art="Heorhiy Narbut’s graphic art.")
W2("IRL", culture="Dublin’s tenements are among the worst slums in Europe.")
W2("CZE", culture="Prague’s Czech National Theatre (1881) and Rudolfinum.", ideas="Social Democrats split along national lines (1911).")
W2("GBR", leaders="David Lloyd George, Chancellor of the Exchequer, and his ‘People’s Budget’ (1909).")
W2("BGR", art="The Bulgarian national style in Sofia’s public buildings.")
W2("ALB", art="Kolë Idromeno’s paintings in Shkodër.")
W2("MNE", culture="Montenegrin men carry arms; blood feuds persist in the highlands.")
W2("FIN", literature="Maria Jotuni and the new women writers.")
W2("DNK", culture="Tivoli and the Copenhagen City Hall (1905).")
W2("ROU", culture="The Romanian Academy (1866) and the Bucharest Athenaeum concerts led by Enescu.")
W2("UKR", ideas="The Union for the Liberation of Ukraine, founded in Lviv in August 1914, hopes for a Central Powers victory.", literature="Volodymyr Vynnychenko’s plays and novels.")
W2("NOR", religion="The state church still oversees parish schools.")
W2("CHE", religion="The Old Catholic church formed after 1870 in opposition to papal infallibility.")
W2("BIH", ideas="Habsburg administrator Benjamin Kállay (1882–1903) promoted a ‘Bosnian’ identity to counter Serb and Croat nationalism.")
W2("IRL", ideas="Larkin and James Connolly’s Irish Citizen Army (1913) gives labour its own militia.")
W2("FIN", culture="Helsinki grows into a modern city of granite banks and offices.")
W2("ESP", leaders="Pablo Iglesias, first Socialist deputy (1910).")
W2("PRT", leaders="Sidónio Pais, minister in Berlin until 1916.")
W2("NLD", leaders="Pieter Jelles Troelstra, Social Democratic leader.")
W2("BEL", leaders="Émile Vandervelde, socialist leader, joins the government in August 1914.")
W2("HUN", leaders="Count Gyula Andrássy the Younger.")
W2("CZE", leaders="Václav Klofáč, National Social leader, arrested in September 1914.")
W2("POL", leaders="Ignacy Daszyński, Galician socialist leader.")
W2("GRC", literature="Angelos Sikelianos’s The Visionary (1909).")
W2("TUR", ideas="The Ottomans abolish the capitulations, foreigners’ legal privileges, in September 1914.")
W2("SRB", religion="Serbian Orthodox Church under the Metropolitan of Belgrade, Dimitrije.")
W2("ITA", leaders="Sidney Sonnino, foreign minister from November 1914.")
W2("SWE", religion="Nathan Söderblom becomes Archbishop of Uppsala in 1914.")
W2("DNK", religion="The Inner Mission revival movement in western Jutland.")
W2("ROU", religion="Greek Catholic and Orthodox Romanians in Transylvania across the border.")
W2("BGR", religion="Muslim Pomaks forcibly converted during the Balkan Wars (1912–13), a policy later reversed.")
W2("ALB", culture="Durrës, the prince’s capital, and Shkodër, the largest town.")
W2("MNE", ideas="The Podgorica-centred opposition favours union with Serbia.")
W2("GBR", culture="The People’s Budget and old-age pensions mark the birth of a welfare state.")
W2("RUS", leaders="War Minister Vladimir Sukhomlinov.")
W2("AUT", leaders="Prime Minister Karl von Stürgkh, governing without parliament from March 1914.")
W2("DEU", leaders="Erich Ludendorff and Paul von Hindenburg, victors at Tannenberg.")
W2("FRA", leaders="War Minister Adolphe Messimy.")
