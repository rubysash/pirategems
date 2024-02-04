# Define some colors
# https://www.rapidtables.com/web/color/
PLAYER = (0, 255, 0)
LIGHT = (255, 255, 153)
UNSEEN = (15, 15, 15)
SEEN = (10, 10, 35)

WHITE = (255, 255, 255)
GREY = (100, 100, 100)
BLACK = (0, 0, 0)

RED = (255,0,0)
ORANGE = (255,165,0)
YELLOW = (255,255,0)
GREEN = (0, 255, 0)
BLUE = (0,0,255)

GOLD = (255,215,0)
VIOLET = (138,43,226)
PINK = (219,112,147)
COUGH = (143,188,143)

# Set the width and height of the screen (width, height).
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
size = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Loop until the user clicks the close button.
game_running = True

# Light range
LIGHT_RANGE = 10

# Generate the maze
ROWS = 75
COLS = 75

# Starting position of the player and light source
player_x = 25
player_y = 25
light_x = player_x
light_y = player_y

# start maze where player is safe
start_x = player_x
start_y = player_y

# scales based on rows/COLS.  (screen width // 75) using floor division
CELL_SIZE = size[0] // max(ROWS, COLS)

# Percentage of monsters appearing per cell
monster_density = 1.0

monster_blink_state = False
crystal_blink_state = True
target_monster = None

# stores if the player has searched the dead monster or not.
# dead monster visibility remains even after this is modified.
dead_monsters = []

got_him_message = False     # for displaying the "Got him!" message
got_him_start_time = 0

# adjust for difficulty
score = 750
crystal_value = 75
exit_value = 500
monster_value = -20
total_crystals = 0
toxicity_value = 100

# for mouse tracking
mouse_x, mouse_y = None, None

# idle score drop
loop_counter = 0
message_end_time = None
message_color = None

paused = True

insults = [
    "To Davy Jones with ye, bilge rat!",
    "Sink to the abyss, ye muck-guzzler!",
    "Rot in hell, ye lily-livered cur!",
    "Go feed the fish, scurvy mongrel!",
    "Stay down, ye flea-bitten swab!",
    "G'night, ye barnacle-brained buffoon!",
    "Rest in the deep, ye blubbering coxcomb!",
    "Off to hell, ye grog-snarfing lubber!",
    "Sleep with the sharks, sea weasel!",
    "Join the damned, ye pockmarked wretch!",
    "Taste the deep, ye slime-covered eel!",
    "To the locker with ye, bilge-sucker!",
    "Sink forever, ye snot-nosed blaggard!",
    "Dream of the deep, yeast-brewed loon!",
    "Stay dead, ye pus-filled sea toad!",
    "Drown in darkness, ye landlubber!",
    "Die twice, ye scallywag scalawag!",
    "Stay buried, ye slobbering barnacle!",
    "Enjoy the abyss, ye rot-smelling rogue!",
    "Good riddance, ye fish-breathed fool!",
    "To hell's heart with ye, cur!",
    "Swim with demons, ye scabrous dog!",
    "Feed the deep, ye gutter-snipe!",
    "Take a nap, ye slack-jawed seabass!",
    "Embrace the void, ye grog-addled git!",
    "Rot away, ye stinky goblin mongrel!",
    "Rest with worms, ye spineless dog!",
    "Back to the abyss, ye swine!",
    "Rest in the deep, ye chum-chewing churl!",
    "Away with ye, ye pox-faced twit!",
    "To the depths, ye sniveling snake!",
    "Dance with devils, ye wormy wretch!",
    "Away to hell, ye snot-gobbling gull!",
    "Lie low, ye salt-soaked imbecile!",
    "G'bye, ye gutless gobshite!",
    "Suffer the deep, ye reeking rat!",
    "Perish, ye pickle-brined parrot!",
    "Fade away, ye floundering fluke!",
    "Dive to darkness, ye damp dolt!",
    "Join the cursed, ye clammy cur!",
    "Rest in ruin, ye rum-sotted rascal!",
    "Linger in the locker, ye limp lubber!",
    "To the abyss, ye algae-addled ape!",
    "Fall forever, ye flea-ridden fraud!",
    "Sink and simmer, ye shoddy shrimp!",
    "Decay in the deep, ye doddering dunce!",
    "Wallow in waste, ye weasel-faced whelp!",
    "Stay in the shadows, ye salty slug!",
    "Breathe the brine, ye barnacled buffoon!",
    "Rot in the reefs, ye rum-riddled ruffian!"
]

cough_banter = [
    "Yarrr, the air's cursed!",
    "Be this a devil's breath?",
    "Me lungs be rebelling!",
    "This air be thicker than grog!",
    "Gaspin' like a fish outta water!",
    "Feels like a shipwreck in me chest.",
    "Can't haul wind!",
    "Darker 'n the depths in here.",
    "Blow me down, need some breeze!",
    "Me lungs be in irons!",
    "Hard to find me sea legs with this air.",
    "Breathin's like haulin' anchor!",
    "By Davy Jones, me chest...",
    "Feels like I'm in the locker!",
    "Cursed sea fog in me lungs!",
    "This ain't the breath of freedom.",
    "Me head's spinnin' like a compass!",
    "Feels like a kraken's got me lungs!",
    "This ain't the pirate's life...",
    "Aye, the air be traitorous.",
    "Blackbeard's ghost, it's murky!",
    "Searchin' for clean wind, but findin' none.",
    "Need to escape this cursed grotto.",
    "Like a storm without an eye, this air.",
    "Coughin' up the abyss...",
    "Bilge rat air, this is!",
    "So wet, might as well be underwater.",
    "What be this? [cough] A curse?",
    "This challenge be harsh.",
    "Feels like the deep's tryin' to drown me.",
    "Like sailin' through a maelstrom.",
    "Every breath's a battle.",
    "Longin' for the open sea's air.",
    "It's as if the sea's in here.",
    "Old and rotten, this air be.",
    "The world's fadin'...",
    "Scarce a good breath to be had.",
    "Breathin's like draggin' anchor.",
    "Like a swamp on a hot day.",
    "Feels like a tightened noose.",
    "Gaspin' like a beached whale.",
    "This air's out to get me.",
    "Breaths as short as a landlubber's voyage.",
    "Yarrr, who corked the air?",
    "Air's fouler than a bilge rat's backside!",
    "Breathe? Might as well drink seawater!",
    "This air's got more bite than a shark!",
    "Feels like breathin' through a barnacle beard!",
    "By Neptune's trident, this ain't fresh!",
    "What be this, air from a dead man's chest?",
    "Like tryin' to sip air from an empty rum bottle!",
    "Methinks this cave's got bad breath!",
    "Breathin's like chewin' on old leather boots!",
    "Who farted? Blackbeard's ghost?",
    "This air ain't fit for even a scurvy dog!",
    "Would rather sniff a sailor's sock!",
    "Lost me wind like a sail in the doldrums.",
    "What curse be this? Breathless I be!",
    "This air's been pickled in sea monster's brine!",
    "As stale as last year's hardtack.",
    "Would trade this for a breath of salty sea wind!",
    "Feels like I've snorted gunpowder!",
    "Cursed caves! Robbin' me of me wind.",
    "Breathin' this is like kissin' a fish's arse!",
    "It's like the cave's got the scurvy.",
    "Worse than wakin' below decks after a night o' rum!",
    "I've smelt cleaner air in a crow's nest latrine!",
    "Yarrr, someone put a cork in this cave?",
    "Like the wind's been stolen by a sea witch.",
    "Aye, I've had grog fresher than this air!",
    "By the Flying Dutchman, where's the wind?",
    "It's like a mermaid's rejected kiss.",
    "Reckon I'm breathin' in a kraken's belch!",
    "Thinner than a plank I'd make ye walk!",
    "Me lungs feel like they've been keelhauled.",
    "Did a sea serpent die in here?",
    "This ain't the sweet kiss of the sea's breeze.",
    "Is this the breath of a thousand ghost pirates?",
    "Would rather be in a barrel of pickled herring!",
    "Feels like a siren's trying to choke me!",
    "This air's been robbed of its freshness!",
    "Even a parrot wouldn't squawk in this.",
    "Got less wind than a ship becalmed!",
    "Blimey, the cave's got halitosis!",
    "Lost in a fog of this rancid breath.",
    "Give me the open sea, not this choking abyss!",
    "Feels like a seaweed salad in me throat.",
    "Like the cave's been gargling grog.",
    "If air were gold, this'd be fool's treasure!",
    "This breeze's been cursed by Davy Jones himself!"
]

found_gem = [
    "Ahoy! A gem worth its salt!",
    "By the stars! What a shiny sight!",
    "Yarrr, a gleam to light up me days!",
    "Blimey! It's a pirate's paradise!",
    "Hoist the flag! We've struck gold!",
    "Shine brighter than a full moon's night!",
    "Blow me down! That's a real beauty!",
    "Yarrr, a gem fit for a sea king!",
    "By the anchor! It's a sight to behold!",
    "Corsair's gem! A true treasure!",
    "Deck and dagger! What a find!",
    "Glinting like a siren's charm!",
    "Aye! It's a buccaneer's bounty!",
    "Mast and marvel! A gem of the sea!",
    "Brighter than the northern star!",
    "Yarrr, a jewel from the ocean's heart!",
    "By the parrot's beak! It's gleaming!",
    "Set the sails, we're rich, mates!",
    "No hornswoggle! A genuine prize!",
    "Sea's secret, now in me grasp!",
    "Gleam like the sun on calm waters!",
    "Jewel worthy of a pirate's tale!",
    "Shanties will sing of this gem!",
    "By the ghost ship! It's mesmerizing!",
    "Pirate's pleasure! A glinting glory!",
    "Avast ye! A treasure for the ages!",
    "Look alive! A marvel from the depths!",
    "Sea's kiss in solid form!",
    "By the compass! It's shining true!",
    "Ahoy! The heart of the abyss found!",
    "Heave ho! It's a sailor's dream!",
    "Rum and radiance! What a sparkle!",
    "Yarrr, it's the gleam of destiny!",
    "By the crow's nest! It's precious!",
    "Sirens' envy! A gem unparalleled!",
    "Yo ho ho! A gleam to behold!",
    "Anchor and allure! Pure brilliance!",
    "Jewel from the cave's hidden heart!",
    "By the helm! A beacon of riches!",
    "Treasure's twinkle in me palm!",
    "Galleon's glow from the dark!",
    "Pirate's prize! Pure and shining!",
    "Buccaneer's bliss in crystal form!",
    "Yarrr, it's the dream of the drift!",
    "Star of the sea, now with me!",
    "Doubloons aside, this's the prize!",
    "A gem's dance in the dark revealed!",
    "By the cutlass! It's gleaming gold!",
    "Sea legend in solid shimmer!",
    "Pirate's path lit by this gem!",
    "Ahoy! What be this gleamin' jewel?",
    "Blimey! That gleam's callin' me name!",
    "Hoist the colors, I've struck gold!",
    "By the seven seas, that's a sight to see!",
    "Shiver me timbers! What a find that be!",
    "Yarrr, that sparkle be like a siren's song!",
    "By me peg-leg, that's a gem worth havin'!",
    "Aye, that glitter! Me heart's all aflutter!",
    "Avast! Be that the heart of the ocean?",
    "In this dark abyss, a glimmer calls to me!",
    "Yarrr, could that be the gem of legends?",
    "By Davy Jones, what a sight to behold!",
    "Ah, the twinkle of a true treasure!",
    "Such brilliance, hidin' in this cavern's gut!",
    "Ahoy! A gem that'd make any buccaneer weep!",
    "By me cutlass, that's a gem worth a king's ransom!",
    "That shimmer! The sea's bounty knows no bounds!",
    "Yarrr, the gleam of me dreams, it be!",
    "Batten down the hatches! What a find!",
    "By the Kraken's tentacles, I've struck it rich!",
    "In the cave's belly, a jewel awaits me grasp!",
    "Dead men tell no tales, but gems surely do!",
    "That glow! A pirate's delight in this dark!",
    "Anchors aweigh! Me gem's in sight!",
    "Yo ho ho! That be the gem I've longed for!",
    "Blow me down! Such a gem amidst these rocks!",
    "Ah, the glint that sets a pirate's heart alight!",
    "Aye, the gleam that promises untold riches!",
    "Splice the mainbrace! The gem's almost in hand!",
    "Yarrr, every twinkle's a step closer to me dream!",
    "Avast! In the dark, a jewel shines the brightest!",
    "By the old salt's tales, that's a gem of yore!",
    "Aye, amidst shadows, a treasure's glow beckons!",
    "In the gloom, one gem stands out like a beacon!",
    "Belay that! Be that the gem of me heart's desire?",
    "By all the rum in the Caribbean, what a find!",
    "Ahoy there! A jewel worthy of a pirate's chest!",
    "Yarrr, me heart beats faster with that glow!",
    "By the sirens' song, that gem's call is strong!",
    "Look lively, mates! A gem's gleam be near!",
    "By the winds of the West, that's a beauty!",
    "Blimey! The sea's whispered tales of such gems!",
    "Aye, that's the gem that legends speak of!",
    "Avast ye! A jewel that'd make a mermaid jealous!",
    "By the depths below, I've found a gem above!",
    "Aye, the whispers of the cave lead to that gleam!",
    "Hoist the sails! The gem of destiny be found!"
]

gross_messages = [
    "Arrgh! Me boots!",
    "Blimey! What be that goo?",
    "By Davy Jones' locker, that's nasty!",
    "Shiver me timbers, what a mess!",
    "Yarrr, that be foul!",
    "By Neptune's beard, what have I stepped in?",
    "Ahoy, me boot's stuck in beastly muck!",
    "Bilge rat! Me foot's fouled!",
    "Kraken's snot! This be vile!",
    "Barnacles! What be this gloop?",
    "By the Jolly Roger, that's repulsive!",
    "Scurvy muck! Me shoes are ruined!",
    "Yo ho no! Not on me boots!",
    "Marauder's mess! What a foul trap!",
    "Blackbeard's ghost, that's putrid!",
    "Booty and beast, not a combo I wanted!",
    "Blow me down, that's some nasty slop!",
    "Landlubber's luck! I've found the filth!",
    "Ahoy, it's a slippery slope to the deep!",
    "Becalmed in beastly bilge!",
    "Cursed creature's gunk!",
    "By the Flying Dutchman, what a vile step!",
    "Matey, me foot's in a right pickle!",
    "Sea dog's drool! I've fouled me step!",
    "Hornswoggle! That's a beastly puddle!",
    "Walk the plank, not the muck!",
    "Pirate's peril! Sludgy shores ahead!",
    "Avast ye, this ain't treasure!",
    "Sea serpent's slime!",
    "By the stars, that's beastly!",
    "Grog's gone sour! What be this mire?",
    "Ahrr! More muck than a sunken galley!",
    "Buccaneer's blunder! Filth underfoot!",
    "Yarrr, that ain't golden sand!",
    "Moby Dick's spit! What a blight!",
    "Dead man's goo! Watch where ye tread!",
    "Anchor's aweigh! And so's me foot!",
    "Pirate's plight! That ain't right!",
    "Corsair's curse! Me boots be doomed!",
    "Harpoons 'n horrors! Filthy depths below!",
    "Boot straps and bilge! I puked in my mouth!",
    "By the crow's nest! It's a nasty nest down here!",
    "Cutlass and crud! A slippery foe!",
    "Mermaid's mire! A treacherous step!",
    "Portside puddle of putrid peril!",
    "Ahrr, not the treasure trove I sought!",
    "Mast and muck! A devilish trap!",
    "Sails and sludge! A filthy voyage for me foot!",
    "Cannons and crud! Beast left a mark!",
    "Peg leg's plight! Would've missed that muck!",
    "Shipwreck's shame! Step with care, matey!",
    "Doubloons and dung! This ain't rich!",
    "Galleon's grime! Me path's gone astray!",
    "Ahoy, abyss of abomination below!",
    "By the seven seas, it's a swampy sorrow!",
    "Marooned in muck! What devilish luck!",
    "Belay the bilge! That's one foul footprint!",
    "Scurvy and slime, a wretched rhyme!",
    "Gold-hunt gone gross! What be this loss?",
    "Matey, map didn't mark this mucky mess!"
]

HELP_COMMANDS = {
    "description": "Ye be the Dread Greybeard, and come lookin fer ye booty. Long ago, ye stashed sparklin' gems from yer plunderin in these cursed caves knowin only a fool would dare venture in. Goblins, being half-wit, sea-rotten, bilge-suckin' bliters and muck-swimmin' mongrels they be, moved into the caves, making the air toxic to breathe. Should yer breathin' (your score) run short, ye'll be meetin' Davy Jones. Ye hid your biggest diamonds deep in the caves, and you swear by the stormy seas that ye be gettin' what be rightly yers. Weigh yer life 'gainst yer lust for gold, matey. Sure as rum's strong and the sea be deep, you be getting your gems!",
    "<numpad>": "movement keys",
    "<tab>": "targets the nearest beast",
    "<space>": "fires your pistol",
    "<p>": "pauses/unpauses game",
    "<shift>+arrow": "Sprint 3 spaces instead of walking 1"
}
