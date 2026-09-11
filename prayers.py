"""Spoken intercession banks. Each prayer picks a different shape and different lines."""

from __future__ import annotations


def detect_needs(feeling: str) -> list[str]:
    text = (feeling or "").lower()
    pairs = (
        ("favor", ("meeting", "boss", "interview", "job", "work", "presentation", "jefe", "reunión", "reunion", "trabajo")),
        ("peace", ("stress", "stressed", "anxious", "anxiety", "afraid", "fear", "worry", "worried", "panic", "ansiedad", "miedo", "preocup", "estres")),
        ("rest", ("overwhelm", "too much", "busy", "pressure", "agotad", "mucho")),
        ("strength", ("tired", "exhausted", "weak", "worn", "cansad")),
        ("wisdom", ("decide", "decision", "unsure", "don't know", "dont know", "confused", "no sé", "decidir")),
        ("comfort", ("grief", "loss", "sad", "hurt", "lonely", "duelo", "triste")),
    )
    needs = [need for need, words in pairs if any(word in text for word in words)]
    return needs[:3] or ["peace", "wisdom"]


def _join(*parts: str) -> str:
    return "\n\n".join(p.strip() for p in parts if p and p.strip())


def _pick(seq, seed: int, salt: int):
    return seq[(seed * 17 + salt * 31) % len(seq)]


def _ctx(name: str, female: bool) -> dict:
    him = "her" if female else "him"
    his = "her" if female else "his"
    he = "she" if female else "he"
    return {
        "name": name,
        "Name": name,
        "him": him,
        "his": his,
        "he": he,
        "He": he.capitalize(),
        "son": "daughter" if female else "son",
        "own": "her" if female else "his",
        "himself": "herself" if female else "himself",
    }


def _fmt(text: str, ctx: dict) -> str:
    return text.format(**ctx)


# --- English, prayed OVER someone ---

EN_OPEN_NAMED = (
    "{Name}, I want to pray for you right now.",
    "Father, we are here. I'm praying for {name}.",
    "Lord Jesus, I come with {name}.",
    "Holy Spirit, come close. I want to pray over {name}.",
    "{Name}. The Lord is near. Let me pray.",
    "Father, before I ask for anything, thank You that {name} belongs to You.",
    "Jesus, You know {name}. I'm going to pray in Your name.",
    "I'm standing with {name} before You, Father.",
)

EN_OPEN_YOU = (
    "I want to pray for you right now.",
    "Father, we are here. I want to pray for you.",
    "Lord Jesus, I come with this one You love.",
    "Holy Spirit, come close. I'm going to pray.",
    "The Lord is near. Let me pray.",
    "Father, before I ask for anything, thank You that this child is Yours.",
    "Jesus, You know him. I'm going to pray in Your name.",
    "I'm standing with you before the Father.",
)

EN_OPEN_FP = (
    "Father, I come to You.",
    "Lord Jesus, I am here.",
    "Holy Spirit, I need You close.",
    "Father, thank You that I can come.",
    "Jesus, I trust You with this day.",
    "God, I don't have pretty words. I have You.",
)

EN_STILL = (
    "There's no rush in this.\nThe Father is not in a hurry.",
    "We don't have to make this neat.\nWe can just come.",
    "You can let your shoulders down a little.\nI'm going to pray.",
    "God has time for this.\nHe has time for you.",
)

EN_SPIRIT = (
    "Holy Spirit, You are here.\nCome even closer.\nRest on {him}.",
    "Spirit of God, fill this moment.\nCounselor.\nFriend.\nBe near {name}.",
    "Come, Holy Spirit.\nNot as an idea.\nAs presence.\nOver {his} mind. Over {his} chest.",
    "Holy Spirit, You know how to pray when we don't.\nPray through me now for {him}.",
)

EN_SEE = (
    "Father, You see {him}.\nYou know this day.\nYou are not far.\nYou hold {him}.",
    "You have had Your eye on {him} since this morning.\nYou have not missed a thing.\nYou are kind.",
    "Father, {he} is not hidden from You.\nNot the quiet parts. Not the heavy parts.\nYou see, and You stay.",
    "Lord, You formed {him}.\nYou know {his} frame.\nYou remember {he} is dust, and You still delight in {him}.",
)

EN_NEEDS = {
    "favor": (
        "Father, You are already ahead of {him}.\nI ask for favor — the kind that is Yours, not performance.\nGive {him} the right words, and the wisdom to wait when words are not needed.\nA steady heart.\nLet {him} listen well.\n{He} does not have to carry the outcome as if it all sat on {his} shoulders.\nYou go before {him}.",
        "Lord, make room for {him}.\nOpen what should open.\nShut what should stay shut.\nGive {him} grace in the eyes of the people in front of {him}.\nClear thought. Clean motives. Courage without striving.\nLet {his} presence be peace, because Yours is.",
        "Jesus, You know how to walk into a room.\nWalk in with {him}.\nAnoint {his} speech.\nGuard {him} from saying too much, or too little.\nLet whatever is true and needed come easily.\nAnd whatever is not needed, let it fall away.",
    ),
    "peace": (
        "And I ask for the peace of Jesus.\nThe peace He said He leaves with us.\nNot as the world gives.\nHoly Spirit, quiet what is loud in {him}.\nMind. Body. The place in the chest that will not sit still.\nLet that peace arrive. Let it stay.",
        "Philippians says the peace of God will guard heart and mind in Christ Jesus.\nI ask for that guard now.\nAround {his} thoughts.\nAround {his} sleep tonight.\nAround the next conversation.\nChrist's own peace, keeping {him}.",
        "Jesus, You spoke peace over storms.\nSpeak it here.\nNot a lecture. A word.\nPeace.\nLet {him} feel the difference between being braced and being held.",
    ),
    "rest": (
        "Father, this has been a lot.\nLift what {he} was never meant to carry alone.\nGive {him} room to breathe.\nMatthew says Your yoke is easy, Your burden light.\nTeach {him} that here.\nRest that is not escape — rest that is You.",
        "Lord, unclench {his} hands.\n{He} does not have to hold the whole thing together.\nYou can hold it.\nGive {him} a Sabbath in the middle of an ordinary hour.",
        "Jesus, come as rest.\nNot later. Now.\nLet {his} nervous system remember it is allowed to stand down in Your presence.",
    ),
    "strength": (
        "Jesus, be {his} strength.\nPaul heard You say, My grace is sufficient.\nPower made perfect in weakness.\nSo we don't pretend {he} is steel.\nWe ask for grace that is enough for today.\nPut life back in {his} spirit.\nThe next faithful step. That's all.",
        "Lord, when {he} feels thin, be the strength underneath.\nNot hype. Help.\nA spine of grace.\nEnergy to do the next right thing, and to leave the rest with You.",
        "Father, strengthen {him} with power in the inner person, as Paul prayed.\nChrist at home in {his} heart.\nRooted. Grounded. Able to stand.",
    ),
    "wisdom": (
        "You said if anyone lacks wisdom, let {him} ask, and You give generously.\nSo I'm asking.\nHoly Spirit, speak.\nShow {him} the way that is Yours.\nA clear mind.\nAnd the courage to follow when You make it plain.",
        "Lord, {he} doesn't need every answer.\n{He} needs the next true step.\nLight for the path, not the whole map.\nGive {him} discernment that feels like peace, not like panic.",
        "Jesus, You are wisdom from God.\nBe that for {him}.\nCut through the noise.\nLet what is Yours stand out simply.",
    ),
    "comfort": (
        "Holy Spirit, Comforter, draw close.\nHold {him}.\nLet {him} know {he} is not forgotten.\nYou are near to the brokenhearted.\nBe that nearness without requiring {him} to explain.\nDon't hurry {him}.\nThe days ahead may be heavy.\nYou stay.",
        "Father of mercies, God of all comfort.\nComfort {him} the way only You can.\nNot with a slogan.\nWith Your own presence.\nSit with {him}.\nJesus wept.\nYou know this country of the heart.\nDon't leave {him} in it alone.",
        "Lord, this is a deep water.\nI don't ask You to make it light before it's time.\nI ask You to be in it with {him}.\nStrength for this day.\nBreath for this hour.\nA place to put the tears.\nYou are close.",
    ),
}

EN_HOLDING = (
    "Holy Spirit, Comforter, draw close to {him}.\n"
    "Hold {him}.\n"
    "You know what this hour is asking of {his} heart.\n"
    "I don't ask You to hurry {him}.\n"
    "I ask You to stay.\n"
    "Near to the brokenhearted.\n"
    "Near when the room is quiet.\n"
    "Near when the thoughts will not sit still.\n"
    "Jesus, You wept.\n"
    "You know this country.\n"
    "Walk it with {him}.\n"
    "Strength for today. Only today.\n"
    "You can carry what {he} cannot.",
    "Father, sit with {him}.\n"
    "The God of all comfort.\n"
    "Not a thin word. Yourself.\n"
    "Let {him} feel that {he} is not forgotten.\n"
    "Not abandoned.\n"
    "Not walking this stretch alone.\n"
    "Cover {his} mind.\n"
    "Cover {his} sleep if sleep will come.\n"
    "And if it will not, be the watchman.\n"
    "Mercy. Presence. Enough for this day.",
    "Lord Jesus, be close enough to touch.\n"
    "We don't have to name everything.\n"
    "You already know.\n"
    "Hold {his} chest when it tightens.\n"
    "Hold the hours {he} cannot see yet.\n"
    "Blessed are those who mourn.\n"
    "Comfort {him}.\n"
    "Don't make {him} perform hope.\n"
    "Just be hope, here.",
)

EN_SCRIPTURE = (
    "Jesus said, Peace I leave with you. My peace I give you.\nI take Him at His word for {name} today.",
    "Romans 8. Nothing can separate {him} from the love of God in Christ Jesus.\nNot this day. Not this feeling.\n{He} is held in that love.",
    "The Lord is {his} shepherd.\n{He} will not want.\nLead {him} beside still waters.\nRestore {his} soul.\nEven here.",
    "Come to Me, all who are weary, Jesus said, and I will give you rest.\nI hold {name} there. Give that rest.",
    "Blessed are those who mourn, for they will be comforted.\nJesus wept.\nYou are not far from {him}.",
    "The God of all comfort, who comforts us in all our trouble.\nComfort {him} that way.\nNot with a slogan. With Yourself.",
    "Cast all your anxiety on Him, because He cares for you.\nSo we do.\nWe put it in Your hands, Father.\nYou care for {him}.",
)

EN_IDENTITY = (
    "Remind {him} who {he} is.\nYours.\nA {son}.\nWanted.\nNot a project. A person You love.",
    "Before {he} is anything else today, {he} is beloved in Christ.\nThat is not a mood. It is a fact.\nLet it settle deeper than the day.",
    "Lord, {he} is not what {he} produces.\n{He} is Yours.\nBought with a price.\nKept.\nLet that be the loudest thing in {him}.",
    "You have called {him} by name.\n{He} is Yours.\nSay it over {him} again until {he} can rest in it.",
)

EN_COVERING = (
    "Jesus, I set Your name over {him}.\nOver {his} mind.\nOver {his} heart.\nOver the hours {he} cannot see yet.",
    "Father, keep {him}.\nHold {him}.\nKeep {his} rest.\nStay close through this day and the next.",
    "I ask You to surround {him}.\nMercy on every side.\nA guarded heart.\nYour presence as covering.",
)

EN_BLESSING = (
    "Lord, Your presence is enough.\nGo with {him}.\nStay with {him}.\nLet {him} remember, in the middle of it, that {he} is held.",
    "Peace over {his} thoughts.\nPeace over {his} body.\nPeace over this day, and the next if {he} needs it.",
    "Kindness in {his} own voice toward {himself}.\nStrength for today only.\nYou can carry tomorrow.",
    "Let goodness and mercy follow {him} today.\nNot as a poster. As a fact {he} walks in.",
)

EN_HANDS = (
    "Father, as if my hands were on {his} shoulders, I pray.\nLet {him} feel that {he} is not standing in this alone.",
    "Lord, I hold {name} before You the way a friend would at the altar.\nReceive {him}. Fill {him}. Send {him}.",
)

EN_HUSH = (
    "Let's not fill this with too many words.\nFather, You are here.\nThat is the first thing.",
    "In the quiet, You are God.\nWe start there.\nThen we pray.",
)

EN_GRATITUDE = (
    "Father, thank You first.\nThank You that {he} woke up in Your mercy.\nThank You that we can come at all.",
    "Before I ask, I want to bless Your name.\nYou are faithful.\nYou have been faithful to {him} before.",
)

EN_TRUST = (
    "Father, we trust You with what we cannot hold.\nYou are able.\nYou are kind.\nYou are here.",
    "I don't have to see the end of this to trust You in the middle.\nNeither does {he}.\nYou are worthy of that.",
    "Into Your hands.\nThat's enough of a plan for now.",
)

EN_LEAVE = (
    "We leave {him} with You.\nThat is the safest place {he} can be.",
    "I stop talking now, Father, and I leave {name} in Your care.\nYou do not drop what You hold.",
    "This prayer ends. Your keeping doesn't.",
)

EN_THANKS = (
    "I thank You that {he} does not walk in alone.\nYou are faithful.\nKeep {him} in Your hand today.",
    "Thank You that You heard this.\nThank You that You were already moving before we asked.\nAmen is our trust, not our ending of You.",
    "Blessed are You, Lord.\nYou have not left {him}.\nYou will not.",
)

EN_PRESENCE = (
    "Lord, I ask You to be near.\nNear is the gift.\nStay with {him}.\nDo not hurry {him}.",
    "Your nearness is {his} good.\nEven if it is quiet, be near.\nThat would be enough, and You give more than enough.",
)

# Last-resort shapes only. Grok writes the real prayer from context.
# "needs" maps to one holding petition — presence, not a work-day collage.
EN_SHAPES = (
    ("open", "hush", "spirit", "holding", "scripture", "presence", "trust", "thanks"),
    ("open", "spirit", "see", "holding", "identity", "leave", "thanks"),
    ("spirit", "open", "holding", "scripture", "covering", "trust", "thanks"),
    ("open", "see", "holding", "hands", "presence", "leave"),
    ("gratitude", "holding", "scripture", "identity", "thanks"),
    ("hands", "holding", "scripture", "blessing", "trust", "leave"),
    ("hush", "see", "holding", "scripture", "presence", "thanks"),
    ("open", "spirit", "holding", "trust", "covering", "leave", "thanks"),
)

FP_SHAPES = (
    ("open", "spirit", "see", "holding", "scripture", "thanks"),
    ("open", "holding", "scripture", "identity", "thanks"),
    ("gratitude", "holding", "presence", "scripture", "trust", "thanks"),
    ("hush", "holding", "identity", "scripture", "thanks"),
    ("open", "scripture", "holding", "blessing", "trust", "thanks"),
)

EN_FP_STILL = (
    "I don't have to rush this.\nI am here with You.",
    "I can come as I am.\nYou already know.",
)

EN_FP_SPIRIT = (
    "Holy Spirit, You are here.\nCome close to me.\nRest on me.",
    "Spirit of God, fill this moment.\nI need You, not just answers.",
)

EN_FP_SEE = (
    "Father, You see me.\nYou know this day.\nYou are not far.\nYou hold me.",
    "I am not hidden from You.\nThank You that I don't have to be impressive to be seen.",
)

EN_FP_NEEDS = {
    "favor": (
        "Father, You are already ahead of me.\nI ask for favor that is Yours, not performance.\nThe right words. A steady heart.\nHelp me listen well.\nI do not have to carry the outcome as if it all depended on me.\nYou go before me.",
        "Jesus, walk in with me.\nAnoint my speech.\nGuard me from saying too much, or too little.\nLet what is true come easily.",
    ),
    "peace": (
        "I ask for the peace of Jesus.\nThe peace He leaves with us.\nQuiet what is loud in me.\nMind. Body. This chest.\nLet it stay.",
        "The peace of God, guarding my heart and mind in Christ Jesus.\nI ask for that guard now.",
    ),
    "rest": (
        "Father, this has been a lot.\nLift what I was never meant to carry alone.\nGive me room to breathe.\nYour yoke. Your pace.",
        "Unclench my hands.\nI do not have to hold the whole thing together.\nYou can.",
    ),
    "strength": (
        "Jesus, be my strength.\nYour grace is enough for today.\nPower in weakness, if that's what I have.\nThe next faithful step.",
        "Strengthen me in the inner person.\nChrist at home in my heart.\nI can stand because You stand with me.",
    ),
    "wisdom": (
        "You said if anyone lacks wisdom, let him ask.\nI am asking.\nHoly Spirit, speak.\nLight for the next step, not the whole map.",
        "Jesus, You are wisdom from God.\nCut through the noise in me.\nMake the way plain enough to walk.",
    ),
    "comfort": (
        "Holy Spirit, Comforter, draw close.\nHold me.\nI am not forgotten.\nSit with me.",
        "Father of mercies, comfort me the way only You can.\nNo slogan. Just You.",
    ),
}

EN_FP_SCRIPTURE = (
    "Jesus said, Peace I leave with you. My peace I give you.\nI receive that.",
    "Nothing can separate me from the love of God in Christ Jesus.\nI stand in that.",
    "The Lord is my shepherd. I shall not want.\nLead me. Restore me.",
    "Come to Me, all who are weary, and I will give you rest.\nI am coming. Give me rest.",
)

EN_FP_IDENTITY = (
    "Remind me who I am.\nYours.\nA {son}.\nWanted.",
    "Before I am anything else today, I am beloved in Christ.\nLet that be louder than this day.",
)

EN_FP_COVERING = (
    "Jesus, I receive Your name over my mind, my mouth, the hours I cannot see yet.",
    "Father, keep me.\nKeep my words.\nKeep my rest.",
)

EN_FP_BLESSING = (
    "Your presence is enough.\nGo with me.\nStay with me.",
    "Peace over my thoughts.\nPeace over my shoulders.\nPeace over the next hour.",
)

EN_FP_THANKS = (
    "Thank You that I do not walk in alone.\nYou are faithful.\nKeep me in Your hand today.",
    "Thank You that You heard this.\nYou were already with me.",
)

EN_FP_TRUST = (
    "I trust You with what I cannot hold.\nYou are able.\nYou are kind.",
    "Into Your hands.\nThat's enough of a plan for now.",
)

EN_FP_LEAVE = (
    "I leave this with You.\nYou do not drop what You hold.",
    "This prayer ends. Your keeping doesn't.",
)

EN_FP_HANDS = (
    "Father, I don't come with a performance.\nI come.",
)

EN_FP_HUSH = (
    "I don't need many words.\nYou are here.\nThat is first.",
)

EN_FP_GRATITUDE = (
    "Father, thank You first.\nThank You that I can come.",
)

EN_FP_PRESENCE = (
    "I ask You to be near.\nDon't hurry me.\nStay.",
)

CLOSE_EN = "In Jesus mighty name, we pray, Amen."
CLOSE_ES = "En el poderoso nombre de Jesús, oramos, amén."


EN_FP_HOLDING = (
    "Holy Spirit, Comforter, draw close.\n"
    "Hold me.\n"
    "I don't ask You to hurry me.\n"
    "I ask You to stay.\n"
    "Near when it is quiet.\n"
    "Near when I cannot find the words.\n"
    "Jesus, You wept.\n"
    "Walk this with me.\n"
    "Strength for today. Only today.",
    "Father, sit with me.\n"
    "The God of all comfort.\n"
    "Not a slogan. Yourself.\n"
    "I am not forgotten.\n"
    "Mercy. Presence. Enough for this day.",
)

EN_MORE = (
    "Father, keep watch over the small things too.\n"
    "The walk into the room.\n"
    "The first breath {he} takes when {he} sits down.\n"
    "The moment after, when {he} wonders how it went.\n"
    "Be in all of it.\n"
    "You are not only God of the crisis. You are God of the ordinary hour.\n"
    "Fill that hour with Your nearness.",
    "Lord Jesus, {he} does not need to become someone else to be kept by You.\n"
    "Keep {him} as {he} is, and grow {him} as You will.\n"
    "Give {him} a gentleness toward {himself}.\n"
    "Give {him} a holy stubbornness to stay with You.\n"
    "And when {he} forgets, remind {him} kindly.",
    "Holy Spirit, I ask for fruit that looks like You.\n"
    "Love, even under pressure.\n"
    "Joy that does not have to be loud.\n"
    "Peace that outlasts the meeting of the day.\n"
    "Patience. Kindness. Self-control.\n"
    "Not as a test. As a gift. Grow them in {him}.",
)

EN_FP_MORE = (
    "Father, keep watch over the small things too.\n"
    "The walk in.\n"
    "The first breath when I sit down.\n"
    "The moment after.\n"
    "Be in all of it.\n"
    "You are God of the ordinary hour.\n"
    "Fill that hour with Your nearness.",
    "Lord Jesus, I do not need to become someone else to be kept by You.\n"
    "Keep me as I am, and grow me as You will.\n"
    "Give me a gentleness toward myself.\n"
    "And when I forget, remind me kindly.",
    "Holy Spirit, grow Your fruit in me.\n"
    "Love. Joy. Peace. Patience. Kindness.\n"
    "Not as a test. As a gift.",
)

ES_MORE = (
    "Padre, cuida también lo pequeño.\n"
    "El entrar.\n"
    "El primer respiro cuando se sienta.\n"
    "El momento después.\n"
    "Está en todo eso.\n"
    "No eres Dios solo de la crisis. Eres Dios de la hora ordinaria.\n"
    "Llena esa hora de Tu cercanía.",
    "Señor Jesús, no necesita volverse otro para ser guardado por Ti.\n"
    "Guárdale como es, y hazle crecer como Tú quieras.\n"
    "Dale suavidad consigo mismo.\n"
    "Y cuando olvide, recuérdaselo con bondad.",
    "Espíritu Santo, pido fruto que se parezca a Ti.\n"
    "Amor, aun bajo presión.\n"
    "Gozo que no tenga que ser ruidoso.\n"
    "Paz que dure más que el día.\n"
    "No como prueba. Como don.",
)

ES_FP_MORE = (
    "Padre, cuida también lo pequeño.\n"
    "El entrar. El respiro. El momento después.\n"
    "Está en todo eso.\n"
    "Llena la hora ordinaria de Tu cercanía.",
    "Jesús, no necesito volverme otro para ser guardado por Ti.\n"
    "Guárdame. Hazme crecer.\n"
    "Cuando olvide, recuérdamelo con bondad.",
)

def _expand(shape: tuple[str, ...], bank: dict, ctx: dict, needs: list[str], seed: int) -> str:
    """One variant per slot. Never dump the whole bank."""
    parts: list[str] = []
    for i, slot in enumerate(shape):
        if slot == "needs":
            seq = bank.get("holding") or ()
            if seq:
                parts.append(_fmt(_pick(seq, seed, 200), ctx))
            continue
        seq = bank.get(slot)
        if not seq:
            continue
        parts.append(_fmt(_pick(seq, seed, i * 13 + 3), ctx))
    parts.append(bank["close"])
    return _join(*parts)


def assemble(payload: dict) -> str:
    spanish = payload.get("language") == "es"
    feeling = payload.get("feeling") or ""
    gender = (payload.get("gender") or "male").strip().lower()
    recipient = payload.get("recipient") or "myself"
    style = payload.get("style") or "pastoral"
    name = (payload.get("recipientName") or payload.get("selfName") or "").strip()
    female = gender == "female"
    seed = sum(ord(ch) for ch in feeling) + int(payload.get("seed") or 0) + len(feeling)
    first_person = style == "firstPerson" and recipient == "myself"

    if spanish:
        return _assemble_es(name, female, recipient, first_person, seed)

    ctx = _ctx(name or "this one", female)
    if first_person:
        ctx["name"] = "me"
        ctx["Name"] = "Me"
        bank = {
            "open": EN_OPEN_FP,
            "still": EN_FP_STILL,
            "spirit": EN_FP_SPIRIT,
            "see": EN_FP_SEE,
            "needs": EN_FP_NEEDS,
            "scripture": EN_FP_SCRIPTURE,
            "identity": EN_FP_IDENTITY,
            "covering": EN_FP_COVERING,
            "blessing": EN_FP_BLESSING,
            "thanks": EN_FP_THANKS,
            "trust": EN_FP_TRUST,
            "leave": EN_FP_LEAVE,
            "hands": EN_FP_HANDS,
            "hush": EN_FP_HUSH,
            "gratitude": EN_FP_GRATITUDE,
            "presence": EN_FP_PRESENCE,
            "holding": EN_FP_HOLDING,
            "more": EN_FP_MORE,
            "close": CLOSE_EN,
        }
        shape = FP_SHAPES[seed % len(FP_SHAPES)]
        return _expand(shape, bank, ctx, [], seed)

    who = name
    if who:
        openings = EN_OPEN_NAMED
        ctx["name"] = who
        ctx["Name"] = who
    else:
        openings = tuple(
            line.replace("{name}", "you").replace("{Name}", "You").replace("this one You love", "you")
            if "{name}" in line or "{Name}" in line
            else line
            for line in EN_OPEN_YOU
        )
        # EN_OPEN_YOU already has no {name} except we handle him in last ones
        openings = EN_OPEN_YOU
        ctx["name"] = "you"
        ctx["Name"] = "you"
        if female:
            openings = tuple(
                s.replace("You know him.", "You know her.").replace("with him", "with her")
                for s in openings
            )
    bank = {
        "open": openings,
        "still": EN_STILL,
        "spirit": EN_SPIRIT,
        "see": EN_SEE,
        "needs": EN_NEEDS,
        "scripture": EN_SCRIPTURE,
        "identity": EN_IDENTITY,
        "covering": EN_COVERING,
        "blessing": EN_BLESSING,
        "thanks": EN_THANKS,
        "trust": EN_TRUST,
        "leave": EN_LEAVE,
        "hands": EN_HANDS,
        "hush": EN_HUSH,
        "gratitude": EN_GRATITUDE,
        "presence": EN_PRESENCE,
        "holding": EN_HOLDING,
        "more": EN_MORE,
        "close": CLOSE_EN,
    }
    shape = EN_SHAPES[seed % len(EN_SHAPES)]
    return _expand(shape, bank, ctx, [], seed)


# --- Spanish ---

ES_OPEN_NAMED = (
    "{Name}, quiero orar por ti ahora.",
    "Padre, aquí estamos. Oro por {name}.",
    "Señor Jesús, vengo con {name}.",
    "Espíritu Santo, acércate. Quiero orar por {name}.",
    "{Name}. El Señor está cerca. Voy a orar.",
    "Padre, antes de pedir, te doy gracias porque {name} es Tuyo.",
)

ES_OPEN_YOU = (
    "Quiero orar por ti ahora.",
    "Padre, aquí estamos. Quiero orar por ti.",
    "Señor Jesús, vengo con este hijo Tuyo.",
    "Espíritu Santo, acércate. Voy a orar.",
    "El Señor está cerca. Voy a orar.",
)

ES_OPEN_FP = (
    "Padre, vengo a Ti.",
    "Señor Jesús, aquí estoy.",
    "Espíritu Santo, necesito que estés cerca.",
    "Padre, gracias porque puedo venir.",
)

ES_STILL = (
    "No hay prisa aquí.\nEl Padre no tiene prisa.",
    "No tenemos que dejar esto perfecto.\nSolo venimos.",
    "Dios tiene tiempo para esto.\nTiene tiempo para ti.",
)

ES_SPIRIT = (
    "Espíritu Santo, Tú estás aquí.\nAcércate más.\nDescansa sobre {él}.",
    "Espíritu de Dios, llena este momento.\nConsolador.\nAmigo.\nQuédate cerca de {name}.",
    "Ven, Espíritu Santo.\nNo como idea.\nComo presencia.",
)

ES_SEE = (
    "Padre, Tú le ves.\nTú conoces este día.\nNo estás lejos.\nTú le sostienes.",
    "Has tenido Tu ojo en {él} desde esta mañana.\nNo se te ha escapado nada.\nEres bueno.",
    "Señor, no está escondido de Ti.\nNi lo callado. Ni lo pesado.\nTú ves, y Te quedas.",
)

ES_NEEDS = {
    "favor": (
        "Padre, Tú ya vas delante de {él}.\nTe pido favor — el Tuyo, no el del rendimiento.\nPalabras justas. Un corazón firme.\nQue escuche bien.\nNo tiene que cargar el resultado como si todo dependiera de {él}.\nTú vas delante.",
        "Jesús, Tú sabes entrar a una sala.\nEntra con {él}.\nUnge su hablar.\nGuárdale de decir de más, o de menos.",
    ),
    "peace": (
        "Te pido la paz de Jesús.\nLa que Él deja con nosotros.\nNo como la da el mundo.\nEspíritu Santo, aquieta lo que está alto en {él}.\nMente. Cuerpo. El pecho.\nQue llegue. Que se quede.",
        "La paz de Dios guardará su corazón y su mente en Cristo Jesús.\nPido esa guardia ahora.",
    ),
    "rest": (
        "Padre, esto ha sido mucho.\nAlivia lo que no le toca cargar {solo}.\nDale espacio para respirar.\nTu yugo. Tu paso.",
        "Suaviza sus manos.\nNo tiene que sostenerlo todo.\nTú puedes.",
    ),
    "strength": (
        "Jesús, sé su fuerza.\nTu gracia le alcanza hoy.\nEl siguiente paso fiel. Eso basta.",
        "Fortalécelo en el hombre interior.\nCristo en su corazón.\nPuede estar de pie porque Tú estás.",
    ),
    "wisdom": (
        "Dijiste que si a alguno le falta sabiduría, que la pida.\nAsí que pido.\nEspíritu Santo, habla.\nLuz para el siguiente paso, no para todo el mapa.",
        "Jesús, Tú eres sabiduría de Dios.\nAtraviesa el ruido.\nHaz claro el camino.",
    ),
    "comfort": (
        "Espíritu Santo, Consolador, acércate.\nSosténle.\nQue sepa que no está {olvidado}.\nTú estás cerca.",
        "Padre de misericordias, consuélale como solo Tú puedes.\nSin lema. Con Tu presencia.",
    ),
}

ES_SCRIPTURE = (
    "Jesús dijo: La paz os dejo. Mi paz os doy.\nMe aferro a esa palabra para {name} hoy.",
    "Romanos 8. Nada podrá separar{lo} del amor de Dios en Cristo Jesús.\nNi este día. Ni este sentir.\nEstá sostenido en ese amor.",
    "El Señor es su pastor.\nNada le faltará.\nGuíale a aguas de reposo.\nRestaura su alma.",
    "Venid a mí todos los que estáis trabajados, dijo Jesús, y yo os haré descansar.\nTraigo a {name}. Dale ese descanso.",
)

ES_IDENTITY = (
    "Recuérdale quién es.\nTuyo.\n{Un} {hijo}.\nDeseado.",
    "Antes de cualquier otra cosa hoy, es amado en Cristo.\nNo es un ánimo. Es un hecho.",
)

ES_COVERING = (
    "Jesús, pongo Tu nombre sobre {él}.\nSobre su mente.\nSobre su boca.\nSobre las horas que aún no ve.",
    "Padre, guárdale.\nGuarda sus palabras.\nGuarda su descanso.",
    "Bendícele al entrar y al salir.\nBendice el trabajo de sus manos.\nQue lo que es Tuyo permanezca.",
)

ES_BLESSING = (
    "Señor, Tu presencia basta.\nVe con {él}.\nQuédate con {él}.",
    "Paz sobre sus pensamientos.\nPaz sobre sus hombros.\nPaz sobre la próxima hora.",
)

ES_THANKS = (
    "Te damos gracias porque no camina {solo}.\nTú eres fiel.\nGuárdale en Tu mano hoy.",
    "Gracias porque has oído.\nGracias porque ya Te movías antes de que pidiéramos.",
)

ES_TRUST = (
    "Padre, confiamos en Ti lo que no podemos sostener.\nTú puedes.\nTú eres bueno.\nTú estás aquí.",
    "En Tus manos.\nEso basta como plan por ahora.",
)

ES_LEAVE = (
    "Le dejamos en Ti.\nEse es el lugar más seguro.",
    "Dejo de hablar, Padre, y dejo a {name} en Tu cuidado.\nTú no sueltas lo que sostienes.",
)

ES_HANDS = (
    "Padre, como si mis manos estuvieran sobre sus hombros, oro.\nQue sienta que no está solo.",
)

ES_HUSH = (
    "No llenemos esto de tantas palabras.\nPadre, Tú estás aquí.\nEso es lo primero.",
)

ES_GRATITUDE = (
    "Padre, primero gracias.\nGracias porque {él} amaneció en Tu misericordia.",
)

ES_PRESENCE = (
    "Señor, Te pido que estés cerca.\nCerca es el don.\nQuédate con {él}.\nNo le apures.",
)

ES_SHAPES = EN_SHAPES

ES_FP_NEEDS = {
    "favor": (
        "Padre, Tú ya vas delante de mí.\nTe pido favor que sea Tuyo.\nPalabras justas. Un corazón firme.\nNo tengo que cargar el resultado. Tú vas delante.",
    ),
    "peace": (
        "Te pido la paz de Jesús.\nAquieta lo que está alto en mí.\nQue se quede.",
    ),
    "rest": (
        "Padre, esto ha sido mucho.\nAlivia lo que no me toca cargar.\nDame espacio para respirar.",
    ),
    "strength": (
        "Jesús, sé mi fuerza.\nTu gracia me alcanza hoy.\nEl siguiente paso fiel.",
    ),
    "wisdom": (
        "Si falta sabiduría, que pida.\nPido.\nEspíritu Santo, habla.",
    ),
    "comfort": (
        "Consolador, acércate.\nSosténme.\nNo estoy {olvidado}.",
    ),
}


def _assemble_es(name, female, recipient, first_person, seed):
    él = "ella" if female else "él"
    lo = "la" if female else "lo"
    solo = "sola" if female else "solo"
    olvidado = "olvidada" if female else "olvidado"
    Un = "Una" if female else "Un"
    hijo = "hija" if female else "hijo"
    ctx = {
        "name": name or "ti",
        "Name": name or "tú",
        "él": él,
        "lo": lo,
        "solo": solo,
        "olvidado": olvidado,
        "Un": Un,
        "hijo": hijo,
    }
    if first_person:
        bank = {
            "open": ES_OPEN_FP,
            "still": ("No tengo que apurarme.\nEstoy aquí contigo.",),
            "spirit": ("Espíritu Santo, Tú estás aquí.\nAcércate a mí.",),
            "see": ("Padre, Tú me ves.\nTú conoces este día.\nTú me sostienes.",),
            "needs": ES_FP_NEEDS,
            "scripture": (
                "Jesús dijo: La paz os dejo. Mi paz os doy.\nLa recibo.",
                "Nada podrá separarme del amor de Dios en Cristo Jesús.",
            ),
            "identity": (f"Recuérdame quién soy.\nTuyo.\n{Un} {hijo}.",),
            "covering": ("Jesús, recibo Tu nombre sobre mi mente y sobre este día.",),
            "blessing": ("Tu presencia basta.\nVen conmigo.\nQuédate.",),
            "thanks": (f"Gracias porque no camino {solo}.\nTú eres fiel.",),
            "trust": ("Confío en Ti lo que no puedo sostener.",),
            "leave": ("Dejo esto en Ti.",),
            "hands": ("Padre, vengo. Solo vengo.",),
            "hush": ("No necesito tantas palabras.\nTú estás aquí.",),
            "gratitude": ("Padre, primero gracias.",),
            "presence": ("Te pido que estés cerca.\nNo me apures.\nQuédate.",),
            "holding": (
                "Espíritu Santo, Consolador, acércate.\nSosténme.\nNo me apures.\nQuédate.\nFuerza para hoy. Solo hoy.",
            ),
            "more": ES_FP_MORE,
            "close": CLOSE_ES,
        }
        shape = FP_SHAPES[seed % len(FP_SHAPES)]
        return _expand(shape, bank, ctx, [], seed)

    openings = ES_OPEN_NAMED if name else ES_OPEN_YOU
    if not female and not name:
        openings = tuple(s.replace("este hijo Tuyo", "este hijo Tuyo") for s in openings)
    if female and not name:
        openings = tuple(s.replace("este hijo Tuyo", "esta hija Tuya") for s in openings)
    bank = {
        "open": openings,
        "still": ES_STILL,
        "spirit": ES_SPIRIT,
        "see": ES_SEE,
        "needs": ES_NEEDS,
        "scripture": ES_SCRIPTURE,
        "identity": ES_IDENTITY,
        "covering": ES_COVERING,
        "blessing": ES_BLESSING,
        "thanks": ES_THANKS,
        "trust": ES_TRUST,
        "leave": ES_LEAVE,
        "hands": ES_HANDS,
        "hush": ES_HUSH,
        "gratitude": ES_GRATITUDE,
        "presence": ES_PRESENCE,
        "holding": (
            "Espíritu Santo, Consolador, acércate a {él}.\n"
            "Sosténle.\n"
            "No le apures.\n"
            "Quédate.\n"
            "Cerca del quebrantado de corazón.\n"
            "Jesús lloró.\n"
            "Camina esto con {él}.\n"
            "Fuerza para hoy. Solo hoy.\n"
            "Tú puedes cargar lo que {él} no puede.",
            "Padre, siéntate con {él}.\n"
            "Dios de toda consolación.\n"
            "No un lema. Tú mismo.\n"
            "Que sepa que no está olvidado.\n"
            "Misericordia. Presencia. Bastante para este día.",
        ),
        "more": ES_MORE,
        "close": CLOSE_ES,
    }
    shape = ES_SHAPES[seed % len(ES_SHAPES)]
    return _expand(shape, bank, ctx, [], seed)
