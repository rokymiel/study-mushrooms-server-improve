from django.contrib.auth import authenticate
from django.contrib.gis.geos import Point
from django.core.files.base import ContentFile
from rest_framework import permissions
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK
from rest_framework.parsers import MultiPartParser
from django.utils.timezone import now
from StudyMushroomsServer.logger import base_logger
from .serializers import *
from PIL import Image
import torch
import torchvision
from GPSPhoto import gpsphoto
import base64

# Create your views here.

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

classnames = sorted(classnames)

model = torchvision.models.resnet50()
model.fc = torch.nn.Linear(model.fc.in_features, len(classnames))
device = torch.device('cpu')
model.load_state_dict(torch.load('nn', map_location=device))
model.eval()
logger = base_logger.getChild('users')


class UserView(ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'mushroom_places', 'notes')


class SingleUserView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination


class PlaceView(ListModelMixin, GenericAPIView):
    serializer_class = PlaceSerializer
    pagination_class = LimitOffsetPagination
    queryset = MushroomPlace.objects.all()
    parser_classes = (MultiPartParser,)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        logger.info("Received request for user's mushroom places")
        user = request.user

        queryset = user.mushroom_places.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        logger.info("Responding normally")
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        logger.info("Received request to add a mushroom place for the user")
        user = request.user
        place = MushroomPlace()
        place.location = Point(request.data.get('location'))
        place.date = now()
        place.image = ContentFile(base64.b64decode(request.data.get('image')))
        place.mushroom = Mushroom.objects.get(classname=request.data.get('classname'))
        place.save()
        user.mushroom_places.add(place)
        user.save()
        return Response("Place at " + str(place.location) + " successfully added", status.HTTP_200_OK)


@api_view(["GET"])
def recognize(self, request, *args, **kwargs):
    image = Image.open(base64.b64decode(request.data.get('image')))
    preprocess = torchvision.transforms.Compose([
        torchvision.transforms.Resize(256),
        torchvision.transforms.CenterCrop(224),
        torchvision.transforms.ToTensor(),
        torchvision.transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    tensor = preprocess(image)
    batch = tensor.unsqueeze(0)

    if torch.cuda.is_available():
        batch = batch.to('cuda')
        model.to('cuda')
    with torch.no_grad():
        output = model(batch)

    probs = torch.nn.functional.softmax(output[0], dim=0)
    res = []
    mushrooms = Mushroom.objects.all()
    for i in range(len(classnames)):
        if probs[i].item().__float__() > 0.01:
            res.append((probs[i].item().__float__(), mushrooms.get(classname=classnames[i])))
    res = sorted(res)
    print(res)
    return Response(data=res, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_auth(request):
    logger.info("Received request to register a user")
    serialized = UserSerializer(data=request.data)

    username = request.data.get('username')
    if User.objects.all().filter(username=username).exists():
        return Response({"error": "Duplicate username"},
                        status=status.HTTP_400_BAD_REQUEST)

    mail = request.data.get('email')
    if User.objects.all().filter(email=mail).exists():
        return Response({"error": "Duplicate email"},
                        status=status.HTTP_400_BAD_REQUEST)

    if serialized.is_valid():

        pswd = request.data.get('password')
        if len(pswd) < 8 or len(pswd) > 30 or not pswd.isalnum():
            logger.error("Invalid new password. Responding with 400")
            return Response({"error": "Invalid password"},
                            status=status.HTTP_400_BAD_REQUEST)

        User.objects.create_user(
            email=request.data.get('email'),
            username=request.data.get('username'),
            password=request.data.get('password')
        )
        logger.info("Registered successfully")
        token, _ = Token.objects.get_or_create(user=User.objects.get(username=username))
        logger.info("Logged in successfully. Returning a token. Responding normally")
        return Response({'token': token.key},
                        status=HTTP_200_OK)

    else:
        logger.error("Failed to register. Responding with 400")
        return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    logger.info("Received request to login")
    username = request.data.get("username")
    password = request.data.get("password")

    if username is None or password is None:
        logger.error("No username or password. Responding with 400")
        return Response({'error': 'No username or password'},
                        status=HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if not user:
        logger.error("Invalid credentials. Responding with 404")
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)

    token, _ = Token.objects.get_or_create(user=user)
    logger.info("Logged in successfully. Returning a token. Responding normally")
    return Response({'token': token.key},
                    status=HTTP_200_OK)


@api_view(["POST"])
def add_place(request):
    logger.info("Received request to add a mushroom place for the user")
    user = request.user
    place = MushroomPlace()
    place.location = Point(request.data.get('location'))
    place.date = now()
    place.image = ContentFile(base64.decodebytes(request.data.get('image')))
    place.mushroom = Mushroom.objects.get(classname=request.data.get('classname'))
    place.save()
    user.mushroom_places.add(place)
    user.save()
    return Response("Place at " + str(place.location) + " successfully added", status.HTTP_200_OK)


class NoteView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    pagination_class = LimitOffsetPagination

    class Meta:
        model = Note
        fields = ('content', 'date', 'user')

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        logger.info("Received request for user's mushroom places")
        user = request.user

        queryset = Note.objects.get(user=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        logger.info("Responding normally")
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        logger.info('Received request to add a note')
        user = request.user
        content = request.data.get('content')
        date = now()
        note = Note()
        note.user = user
        note.date = date
        note.content = content
        note.save()
