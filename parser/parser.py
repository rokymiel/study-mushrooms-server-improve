from bs4 import BeautifulSoup
import requests
import re

from parser.managers import MushroomsManager

base_urls = [('https://wikigrib.ru/vidy/sedobnye-griby/', 'edible'),
             ('https://wikigrib.ru/vidy/uslovno-sedobnye/', 'halfedible'),
             ('https://wikigrib.ru/vidy/nesedobnye-griby/', 'inedible')]
classnames = ['Clavulinopsis helvola', 'Agaricus sylvaticus', 'Lactarius glyciosmus', 'Lactarius trivialis',
              'Lentinus substrictus', 'Amanita phalloides', 'Pholiota gummosa', 'Tricholoma columbetta',
              'Agaricus xanthodermus', 'Rubroboletus legaliae', 'Leccinum vulpinum', 'Cystoderma amianthinum',
              'Mycena inclinata', 'Phallus impudicus', 'Hebeloma crustuliniforme', 'Cortinarius trivialis',
              'Ramaria botrytis', 'Tricholoma batschii', 'Echinoderma asperum', 'Cortinarius delibutus',
              'Rhizina undulata', 'Byssonectria terrestris', 'Pluteus pellitus', 'Lactarius deterrimus',
              'Chlorophyllum rhacodes', 'Pholiota highlandensis', 'Agaricus sylvicola', 'Gyroporus castaneus',
              'Peziza badia', 'Lepista saeva', 'Trichaptum abietinum', 'Ganoderma lucidum', 'Pycnoporellus fulgens',
              'Gliophorus irrigatus', 'Hygrocybe ceracea', 'Lyophyllum fumosum', 'Thelephora caryophyllea',
              'Cortinarius largus', 'Mycena haematopus', 'Helvella lacunosa', 'Russula adusta', 'Entoloma clypeatum',
              'Cystoderma carcharias', 'Gyromitra gigas', 'Coltricia perennis', 'Geastrum schmidelii',
              'Agaricus moelleri', 'Picipes badius', 'Buglossoporus quercinus', 'Bjerkandera fumosa',
              'Psathyrella corrugis', 'Sarcoscypha austriaca', 'Russula betularum', 'Cortinarius balteatocumatilis',
              'Pseudoplectania nigrella', 'Cantharellus amethysteus', 'Pleurotus pulmonarius', 'Leucocybe candicans',
              'Hydnellum ferrugineum', 'Paxillus involutus', 'Armillaria mellea', 'Phellodon connatus',
              'Phellodon niger', 'Agaricus campestris', 'Trametes ochracea', 'Conocybe albipes',
              'Humaria hemisphaerica', 'Tricholoma portentosum', 'Tapinella atrotomentosa', 'Lepiota brunneoincarnata',
              'Tyromyces chioneus', 'Cudonia circinans', 'Cystodermella cinnabarina', 'Phellinus lundellii',
              'Pholiota tuberculosa', 'Picipes melanopus', 'Agaricus comtulus', 'Boletus reticulatus',
              'Hymenochaete rubiginosa', 'Asterophora lycoperdoides', 'Stereum rugosum', 'Armillaria ostoyae',
              'Bolbitius titubans', 'Amanita gemmata', 'Hortiboletus rubellus', 'Mycena galopus', 'Inocybe lacera',
              'Amanita ceciliae', 'Tricholoma saponaceum', 'Ceratiomyxa fruticulosa', 'Aureoboletus projectellus',
              'Hygrophoropsis aurantiaca', 'Xerula pudens', 'Leccinum variicolor', 'Mycena pura', 'Clitocybe fragrans',
              'Panellus stipticus', 'Crepidotus applanatus', 'Clitopilus prunulus', 'Caloboletus radicans',
              'Pluteus semibulbosus', 'Cyanoboletus pulverulentus', 'Tulostoma brumale', 'Xylaria polymorpha',
              'Hygrophorus persoonii', 'Hygrocybe punicea', 'Amanita crocea', 'Infundibulicybe geotropa',
              'Gomphidius glutinosus', 'Inocybe geophylla', 'Ascocoryne sarcoides', 'Pluteus petasatus',
              'Scleroderma citrinum', 'Tremella encephala', 'Entoloma conferendum', 'Psathyrella candolleana',
              'Amanita franchetii', 'Spathularia flavida', 'Ciboria amentacea', 'Clitocybe vibecina',
              'Tarzetta cupularis', 'Exobasidium vaccinii', 'Daedalea quercina', 'Gyroporus cyanescens',
              'Cortinarius uliginosus', 'Tricholoma pessundatum', 'Pluteus umbrosus', 'Cortinarius armillatus',
              'Pleurotus ostreatus', 'Tricholoma album', 'Nectria cinnabarina', 'Heterobasidion annosum',
              'Pluteus ephebeus', 'Suillus collinitus', 'Laccaria laccata', 'Bovista plumbea', 'Polyporus tuberaster',
              'Helvella elastica', 'Clitocybe phyllophila', 'Peziza vesiculosa', 'Paralepista flaccida',
              'Ischnoderma resinosum', 'Panus conchatus', 'Thelephora penicillata', 'Inocybe acuta',
              'Agaricus arvensis', 'Laccaria bicolor', 'Lactarius blennius', 'Amanita muscaria', 'Hygrocybe miniata',
              'Auriscalpium vulgare', 'Coprinopsis romagnesiana', 'Phlebia rufa', 'Cortinarius caerulescens',
              'Tricholoma equestre', 'Suillus cavipes', 'Hygrocybe conica', 'Strobilurus esculentus',
              'Laccaria amethystina', 'Suillellus luridus', 'Caloboletus calopus', 'Mycena polygramma',
              'Mycena zephirus', 'Lactarius porninsis', 'Lactarius camphoratus', 'Pseudoinonotus dryadeus',
              'Inonotus hispidus', 'Gyrodon lividus', 'Calocybe gambosa', 'Laetiporus sulphureus', 'Boletus pinophilus',
              'Cortinarius purpurascens', 'Pseudoboletus parasiticus', 'Suillellus queletii', 'Trametes versicolor',
              'Entoloma lividoalbum', 'Tubaria furfuracea', 'Leucoagaricus leucothites', 'Agrocybe pediades',
              'Tricholoma matsutake', 'Agrocybe dura', 'Scutellinia scutellata', 'Hypholoma capnoides',
              'Gymnopus aquosus', 'Disciotis venosa', 'Hygrophorus pustulatus', 'Exidia recisa', 'Tremella mesenterica',
              'Tricholoma stiparophyllum', 'Pholiota flammans', 'Macrolepiota procera', 'Phaeoclavulina abietina',
              'Lactarius controversus', 'Entoloma vernum', 'Clavulina rugosa', 'Chondrostereum purpureum',
              'Leucoagaricus nympharum', 'Calocera viscosa', 'Cortinarius rubellus', 'Cortinarius sanguineus',
              'Cyathus olla', 'Craterellus tubaeformis', 'Helvella crispa', 'Cortinarius multiformis',
              'Laccaria proxima', 'Xerocomellus chrysenteron', 'Mycena acicula', 'Tylopilus felleus',
              'Fomitopsis pinicola', 'Hygrocybe chlorophana', 'Xylaria longipes', 'Boletus edulis', 'Lactarius necator',
              'Cortinarius violaceus', 'Gyromitra esculenta', 'Auricularia auricula-judae', 'Leccinum scabrum',
              'Mitrula paludosa', 'Geastrum fimbriatum', 'Melanoleuca brevipes', 'Hygrophorus agathosmus',
              'Inonotus obliquus', 'Xerocomellus pruinatus', 'Tubifera ferruginosa', 'Pholiota lenta',
              'Hydnum repandum', 'Cortinarius croceus', 'Megacollybia platyphylla', 'Suillus bovinus',
              'Hypholoma marginatum', 'Lycoperdon echinatum', 'Kuehneromyces mutabilis', 'Russula nigricans',
              'Homophron spadiceum', 'Psathyrella spadiceogrisea', 'Russula delica', 'Cortinarius traganus',
              'Fistulina hepatica', 'Hericium cirrhatum', 'Hydnellum aurantiacum', 'Galerina paludosa',
              'Cerioporus squamosus', 'Lactarius tabidus', 'Russula emetica', 'Galerina hypnorum', 'Russula decolorans',
              'Thelephora terrestris', 'Hypholoma fasciculare', 'Mycetinis scorodonius', 'Hydnellum concrescens',
              'Cortinarius pholideus', 'Pucciniastrum areolatum', 'Gliophorus psittacinus', 'Fuligo septica',
              'Coprinellus domesticus', 'Stropharia aeruginosa', 'Ganoderma resinaceum', 'Hypholoma elongatum',
              'Entoloma sepium', 'Amanita excelsa', 'Naucoria subconspersa', 'Lycoperdon nigrescens',
              'Paralepista gilva', 'Volvariella surrecta', 'Daedaleopsis confragosa', 'Marasmius oreades',
              'Gymnopus dryophilus', 'Morchella semilibera', 'Scleroderma areolatum', 'Panellus mitis',
              'Cortinarius caperatus', 'Entoloma asprellum', 'Russula grata', 'Lactarius azonites',
              'Tricholoma vaccinum', 'Lactarius pallidus', 'Trametes hirsuta', 'Aurantiporus fissilis',
              'Tricholoma imbricatum', 'Suillus viscidus', 'Leotia lubrica', 'Skeletocutis carneogrisea',
              'Tricholomopsis rutilans', 'Clitocybe nebularis', 'Crepidotus variabilis', 'Clitocybe rivulosa',
              'Hygrocybe turunda', 'Clitocybe metachroa', 'Entoloma sericeum', 'Lyophyllum decastes',
              'Coprinus comatus', 'Tapinella panuoides', 'Lactarius lignyotus', 'Russula xerampelina',
              'Porphyrellus porphyrosporus', 'Calocera cornea', 'Coprinopsis lagopus', 'Exidia saccharina',
              'Mycena rosea', 'Russula queletii', 'Cantharellus cibarius', 'Entoloma rhodopolium', 'Phlebia tremellosa',
              'Strobilurus tenacellus', 'Russula ochroleuca', 'Lactarius aurantiacus', 'Helvella macropus',
              'Tricholoma frondosae', 'Hebeloma mesophaeum', 'Agaricus bisporus', 'Tricholoma populinum',
              'Entoloma cetratum', 'Russula fragilis', 'Cyclocybe erebia', 'Coprinellus micaceus',
              'Crinipellis scabella', 'Neolentinus lepideus', 'Pseudoclitocybe cyathiformis', 'Lactarius serifluus',
              'Suillus variegatus', 'Cortinarius semisanguineus', 'Tricholoma albobrunneum', 'Tricholoma terreum',
              'Inocybe rimosa', 'Verpa conica', 'Strobilurus stephanocystis', 'Ampulloclitocybe clavipes',
              'Xerocomellus porosporus', 'Lactarius helvus', 'Stereum hirsutum', 'Amanita strobiliformis',
              'Deconica montana', 'Cortinarius alboviolaceus', 'Gomphidius maculatus', 'Leucocoprinus brebissonii',
              'Russula virescens', 'Psathyrella piluliformis', 'Lepista nuda', 'Cortinarius anomalus',
              'Amanita rubescens', 'Daldinia concentrica', 'Russula vesca', 'Psathyrella cotonea', 'Russula aeruginea',
              'Chroogomphus rutilus', 'Phlebia radiata', 'Melanoleuca grammopodia', 'Cordyceps militaris',
              'Pluteus cervinus', 'Morchella esculenta', 'Agaricus bitorquis', 'Lactarius chrysorrheus',
              'Exidia glandulosa', 'Amanita virosa', 'Gomphidius roseus', 'Lepiota subincarnata', 'Amanita fulva',
              'Mycetinis alliaceus', 'Gymnopus peronatus', 'Tricholoma sulphureum', 'Flammulina velutipes',
              'Cerioporus varius', 'Craterellus cornucopioides', 'Hericium erinaceus', 'Cortinarius bolaris',
              'Cortinarius triumphans', 'Meripilus giganteus', 'Lactarius vietus', 'Lepiota cristata',
              'Lycoperdon excipuliforme', 'Lycoperdon perlatum', 'Ascocoryne cylichnium', 'Macrolepiota excoriata',
              'Thelephora palmata', 'Cortinarius cinnamomeus', 'Russula foetens', 'Gymnopus confluens',
              'Ramaria formosa', 'Lycoperdon pyriforme', 'Lepiota castanea', 'Trametes gibbosa', 'Hygrophorus eburneus',
              'Mycena vulgaris', 'Gliophorus laetus', 'Suillus granulatus', 'Kretzschmaria deusta',
              'Cheilymenia granulata', 'Schizophyllum commune', 'Cuphophyllus virgineus', 'Fomes fomentarius',
              'Phylloporus pelletieri', 'Stereum subtomentosum', 'Entoloma sinuatum', 'Lepista sordida',
              'Bulgaria inquinans', 'Pleurotus dryinus', 'Bovista nigrescens', 'Amanita pantherina',
              'Exidiopsis effusa', 'Gloeophyllum sepiarium', 'Lactarius fulvissimus', 'Hydnum albidum',
              'Gymnopilus penetrans', 'Otidea onotica', 'Rubroboletus satanas', 'Cortinarius vernus', 'Amanita citrina',
              'Hygrocybe acutoconica', 'Pluteus leoninus', 'Lentinellus cochleatus', 'Postia caesia',
              'Agaricus bernardii', 'Entoloma euchroum', 'Helvella acetabulum', 'Scleroderma verrucosum',
              'Exidia nigricans', 'Tricholoma fulvum', 'Russula integra', 'Xeromphalina campanella', 'Cyathus striatus',
              'Lactarius pubescens', 'Phaeolepiota aurea', 'Reticularia lycoperdon', 'Lepista irina',
              'Galerina marginata', 'Tricholoma ustale', 'Amanita vaginata', 'Cuphophyllus pratensis',
              'Clavariadelphus pistillaris', 'Inocybe assimilata', 'Lepiota clypeolaria', 'Sarcoscypha coccinea',
              'Lactarius rufus', 'Leucocybe connata', 'Coprinopsis atramentaria', 'Hebeloma sinapizans',
              'Agaricus subperonatus', 'Panaeolus papilionaceus', 'Peziza varia', 'Gymnopus ocior', 'Lactarius quietus',
              'Chalciporus piperatus', 'Hygrocybe quieta', 'Tricholomopsis decora', 'Protostropharia semiglobata',
              'Imleria badia', 'Galerina vittiformis', 'Xylaria hypoxylon', 'Phyllotopsis nidulans',
              'Pluteus hispidulus', 'Hygrophorus olivaceoalbus', 'Amanita porphyria', 'Hericium coralloides',
              'Russula aurea', 'Marasmiellus ramealis', 'Hygrophorus chrysodon', 'Lentinus brumalis',
              'Pseudohydnum gelatinosum', 'Clavulina coralloides', 'Lepiota magnispora', 'Cortinarius collinitus',
              'Russula claroflava', 'Marasmius rotula', 'Psilocybe semilanceata', 'Suillus luteus',
              'Bjerkandera adusta', 'Phaeolus schweinitzii', 'Cortinarius mucosus', 'Mycena filopes',
              'Auricularia mesenterica', 'Grifola frondosa', 'Cerrena unicolor', 'Lentinellus ursinus',
              'Hypholoma lateritium', 'Leccinum versipelle', 'Leccinum quercinum', 'Phellodon tomentosus',
              'Tricholoma scalpturatum', 'Volvariella bombycina', 'Cortinarius hemitrichus', 'Leccinum duriusculum',
              'Hemileccinum impolitum', 'Butyriboletus appendiculatus', 'Hygrocybe coccinea', 'Cystolepiota seminuda',
              'Leccinum albostipitatum', 'Agrocybe praecox', 'Hebeloma radicosum', 'Spinellus fusiger',
              'Crepidotus mollis', 'Suillus grevillei', 'Trichaptum fuscoviolaceum', 'Sparassis crispa',
              'Lactarius mammosus', 'Parasola plicatilis', 'Russula illota', 'Coprinellus disseminatus',
              'Pholiota squarrosa', 'Mycena epipterygia', 'Gymnopus fusipes', 'Inocybe napipes', 'Coprinopsis picacea',
              'Mutinus caninus', 'Ophiocordyceps entomorrhiza', 'Cantharellus pallens', 'Aleuria aurantia',
              'Mycena galericulata', 'Ganoderma applanatum', 'Fomitiporia robusta', 'Abortiporus biennis',
              'Lactarius deliciosus', 'Agaricus augustus', 'Pluteus salicinus', 'Russula paludosa',
              'Pycnoporus cinnabarinus', 'Lactarius subdulcis', 'Chlorociboria aeruginascens', 'Amyloporia sinuosa',
              'Pluteus phlebophorus', 'Agaricus essettei']


def read_name_and_classname(article):
    try:
        name = article.find('h2').string
        classname = name[name.index('(') + 1:name.index(')')]
    except Exception:
        head = article.find('h2')
        name = head.get_text()
        classname = name[name.index('(') + 1:name.index(')')]
    return name, classname


def read_picture_link(article, soup):
    try:
        picture_link = soup.find('div', {'class': 'google_imgs'}).find('href')
    except:
        picture_link = article.find('img')['src']
    if picture_link is None:
        picture_link = article.find('img')['src']
    return picture_link


def read_description(article):
    k = filter(None.__ne__, [el.string for el in article.findAll('p')])
    try:
        description = article.text
    except:
        description = "\n".join(k)
    return description


def read_soup_and_article(item):
    # ex. "https://wikigrib.ru/ejovik-belyj/"
    soup = BeautifulSoup(requests.get(item, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    }).content, 'html.parser')
    article = soup.find('div', {'class': 'entry'})

    return soup, article


def read_links(url, page_num):
    page = requests.get(url + 'page/' + str(page_num), headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    })
    page_soup = BeautifulSoup(page.content, 'html.parser')
    mushroom_list = page_soup.find('div', {'class': 'catcont-list'})

    if mushroom_list is None:
        return None

    return list(
        map(lambda x: x.find('a').get('href'),
            mushroom_list.findAll('section', {'class': re.compile('post post*')})))


def load_mushrooms(base_urls, classnames, m_manager):
    m_manager.reset_mushrooms()

    error_links = []
    for url, type in base_urls:
        for i in range(1, 100):
            links = read_links(url, i)

            if links is None: break

            for item in links:
                print("link:", item)

                try:
                    soup, article = read_soup_and_article(item)
                    name, classname = read_name_and_classname(article)

                    if classname not in classnames:
                        continue

                    picture_link = read_picture_link(article, soup)
                    description = read_description(article)

                    m_manager.save_new_mushroom(name, classname, picture_link, description, type)
                except Exception:
                    print('exc caught')
                    error_links.append(item)


if __name__ == "__main__":
    load_mushrooms(base_urls, classnames, MushroomsManager())
