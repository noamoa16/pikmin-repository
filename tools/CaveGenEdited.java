// CaveGen.CaveGenを以下で置き換える

public CaveGen() {
    caveGenInit();

    HashMap<String, Integer> counter = new HashMap<>();

    for (int i = 0; i < numToGenerate; i++) {
        caveGenStep(i);
        
        String key;
        if(
            (specialCaveInfoName.equals("FC") && sublevel == 4) ||
            (specialCaveInfoName.equals("BK") && sublevel == 6) ||
            (specialCaveInfoName.equals("GK") && sublevel == 5) ||
            (specialCaveInfoName.equals("SR") && sublevel == 5)
            ){
            boolean murasakipom = false;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("BlackPom")){
                    murasakipom = true;
                }
            }
            key = "{murasakipom: " + murasakipom + "}";
        }
        else if(
            (specialCaveInfoName.equals("FC") && sublevel == 7) ||
            (specialCaveInfoName.equals("SC") && sublevel == 4)
            ){
            boolean oogane = false;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("Wealthy")){
                    oogane = true;
                }
            }
            key = "{oogane: " + oogane + "}";
        }
        else if(specialCaveInfoName.equals("SCx") && sublevel == 4){
            int whitepom = 0;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("WhitePom")){
                    whitepom++;;
                }
            }
            key = "{whitepom: " + whitepom + "}";
        }
        else if(specialCaveInfoName.equals("SCx") && sublevel == 7){
            boolean fixedTamakokin = false;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("FminiHoudai")){
                    fixedTamakokin = true;
                }
            }
            key = "{fixedTamakokin: " + fixedTamakokin + "}";
        }
        else if(specialCaveInfoName.equals("BK") && sublevel == 4){
            int murasakipom = 0;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("BlackPom")){
                    murasakipom++;
                }
            }
            key = "{murasakipom: " + murasakipom + "}";
        }
        else if(specialCaveInfoName.equals("CoS") && sublevel == 3){
            boolean popogashi = false;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("RandPom")){
                    popogashi = true;
                }
            }
            key = "{popogashi: " + popogashi + "}";
        }
        else if(specialCaveInfoName.equals("CoS") && sublevel == 4){
            boolean chocolate = false;
            for(Teki teki : placedTekis){
                if(
                    teki.tekiName.equals("Jigumo") && 
                    teki.itemInside != null &&
                    teki.itemInside.equals("chocolate")
                    ){
                    chocolate = true;
                }
            }
            key = "{chocolate: " + chocolate + "}";
        }
        else if(specialCaveInfoName.equals("GK") && sublevel == 3){
            boolean yellowpom = false;
            boolean castanets = false;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("YellowPom")){
                    yellowpom = true;
                }
            }
            for(Item item : placedItems){
                if(item.itemName.equals("castanets")){
                    castanets = true;
                }
            }
            key = "{yellowpom: " + yellowpom + "}";
            counter.put(key, counter.getOrDefault(key, 0) + 1);
            key = "{castanets: " + castanets + "}";
        }
        else if(specialCaveInfoName.equals("SR") && sublevel == 6){
            boolean onarashi = false;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("Fart")){
                    onarashi = true;
                }
            }
            key = "{onarashi: " + onarashi + "}";
        }
        else if(specialCaveInfoName.equals("SR") && sublevel == 7){
            boolean kemekuji = false;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("UmiMushi")){
                    kemekuji = true;
                }
            }
            key = "{kemekuji: " + kemekuji + "}";
            if(!kemekuji){
                System.out.println(String.format("0x%08X", firstGenSeed + i));
            }
        }
        else if(specialCaveInfoName.equals("CH2") && sublevel == 2){
            int mitites = 0;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("TamagoMushi")){
                    mitites++;
                }
            }
            key = "{mitites: " + mitites + "}";
        }
        else if(specialCaveInfoName.equals("CH5") && sublevel == 2){
            int eggs = 0;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("Egg")){
                    eggs++;
                }
            }
            key = "{eggs: " + eggs + "}";
        }
        else if(specialCaveInfoName.equals("CH8") && sublevel == 1){
            int kocha = 0;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("Kochappy")){
                    kocha++;
                }
            }
            key = "{kocha: " + kocha + "}";
            if(kocha <= 3){
                System.out.println(String.format("kocha = %d, seed = 0x%08X", kocha, firstGenSeed + i));
            }
        }
        else if(specialCaveInfoName.equals("CH18") && sublevel == 1){
            int eggs = 0;
            boolean yakicha = false;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("Egg")){
                    eggs++;
                }
                else if(teki.tekiName.equals("FireChappy")){
                    yakicha = true;
                }
            }
            key = "{eggs: " + eggs + "}";
            counter.put(key, counter.getOrDefault(key, 0) + 1);
            key = "{yakicha: " + yakicha + "}";
            if(eggs >= 7){
                System.out.println(String.format("eggs = %d, seed = 0x%08X", eggs, firstGenSeed + i));
            }
        }
        else if(specialCaveInfoName.equals("CH20") && sublevel == 1){
            int eggs = 0;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("Egg")){
                    eggs++;
                }
            }
            key = "{eggs: " + eggs + "}";
            if(eggs >= 5){
                System.out.println(String.format("eggs = %d, seed = 0x%08X", eggs, firstGenSeed + i));
            }
        }
        else if(specialCaveInfoName.equals("CH21") && sublevel == 1){
            int bikkuri = 0, haori = 0, oogane = 0, ujimesu = 0, ujiosu = 0, tobinko = 0;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("Hana")){
                    bikkuri++;
                }
                else if(teki.tekiName.equals("Armor")){
                    haori++;
                }
                else if(teki.tekiName.equals("Wealthy")){
                    oogane++;
                }
                else if(teki.tekiName.equals("UjiA")){
                    ujimesu++;
                }
                else if(teki.tekiName.equals("UjiB")){
                    ujiosu++;
                }
                else if(teki.tekiName.equals("Tobi")){
                    tobinko++;
                }
            }
            if(bikkuri != 2 || haori != 3 || oogane != 1){
                System.out.println(String.format(
                    "bikkuri = %d, haori = %d, oogane = %d, ujimesu = %d, ujiosu = %d, tobinko = %d",
                    bikkuri, haori, oogane, ujimesu, ujiosu, tobinko
                ));
            }
            key = "{ujimesu: " + ujimesu + ", ujiosu: " + ujiosu + ", tobinko: " + tobinko + "}";
        }
        else if(specialCaveInfoName.equals("CH26") && sublevel == 3){
            int eggs = 0;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("Egg")){
                    eggs++;
                }
            }
            key = "{eggs: " + eggs + "}";
            if(eggs >= 10){
                System.out.println(String.format("eggs = %d, seed = 0x%08X", eggs, firstGenSeed + i));
            }
        }
        else if(specialCaveInfoName.equals("CH28") && sublevel == 1){
            int eggs = 0;
            boolean elec = false;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("Egg")){
                    eggs++;
                }
                else if(teki.tekiName.equals("ElecOtakara")){
                    elec = true;
                }
            }
            key = "{eggs: " + eggs + ", elec: " + elec + "}";
            counter.put(key, counter.getOrDefault(key, 0) + 1);
            boolean geyser = placedGeyser != null;
            key = "{geyser: " + geyser + "}";
        }
        else if(specialCaveInfoName.equals("CH29") && sublevel == 1){
            int eggs = 0;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("Egg")){
                    eggs++;
                }
            }
            key = "{eggs: " + eggs + "}";
            if(eggs >= 7){
                System.out.println(String.format("eggs = %d, seed = 0x%08X", eggs, firstGenSeed + i));
            }
        }
        else{
            throw new UnsupportedOperationException(specialCaveInfoName + "-" + sublevel);
        }
        counter.put(key, counter.getOrDefault(key, 0) + 1);
    }

    String result = String.format("{\"seed\": 0x%08X, \"num\": 0x%08X, \"result\": {", firstGenSeed, numToGenerate);
    int i = 0;
    for(Map.Entry<String, Integer> entry : counter.entrySet()){
        if(i != 0){
            result += ", ";
        }
        result += "\"" + entry.getKey() + "\"" + ": " + entry.getValue();
        i++;
    }
    result += "}}";
    System.out.println(result);

    caveGenEnd();
}

private void caveGenInit(){
    specialCaveInfoName = Parser.toSpecial(caveInfoName);
    if (storyModeOverride)
        hardMode = true;
    else if (challengeModeOverride)
        hardMode = false;
    else {
        hardMode = !specialCaveInfoName.substring(0,2).equalsIgnoreCase("CH");
    }
    challengeMode = !hardMode;

    new Parser().parseAll(this); // Parse everything
    if (isFinalFloor) holeClogged = !isHardMode(); // final floor geysers aren't clogged in story mode

    if (aggregator) {
        Aggregator.reset();
    }
    if (judgeActive) {
        stats.judge.setupJudge(this);
    }
}

private void caveGenStep(int i){
    indexBeingGenerated = i;
    if (seedOrder) {
        initialSeed = (int)seedCalc.next_seed(firstGenSeed, i);
    }
    else {
        initialSeed = firstGenSeed + i;
    }
    seed = initialSeed;

    if (prints && (numToGenerate < 4096 && !CaveGen.judgeActive || initialSeed % 4096 == 0)) {
        System.out.println("Generating " + specialCaveInfoName + "-" + sublevel + " on seed " + Drawer.seedToString(initialSeed));
        if (CaveViewer.active) {
            CaveViewer.caveViewer.reportBuffer.append("Generating " + specialCaveInfoName + "-" + sublevel + " on seed " + Drawer.seedToString(initialSeed) + "\n");
        }
    }

    reset();

    if (readMemo) {
        memo.readMemo(this);
    } else {
        createRandomMap();
    }

    if (showStats && !shortCircuitMap) {
        try {
            stats.analyze(this);
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(0);
        }
    }
    if (images && !shortCircuitMap && imageToggle) {
        try {
            drawer.draw(this);
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(0);
        }
    }
    if (expectTest) {
        memo.outputSublevelForExpect(this);
    }
    if (writeMemo) {
        memo.writeMemo(this);
    }
    if (aggregator) {
        Aggregator.process(this);
    }
    if (CaveViewer.active) {
        CaveViewer.caveViewer.update();
    }
}

private void caveGenEnd(){
    if (showCaveInfo) {
        try {
            drawer.drawCaveInfo(this);
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(0);
        }
    }
    if (aggregator) {
        try {
            drawer.drawAggregator(this);
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(0);
        }
    }
    if (judgeActive && !judgeCombine) {
        stats.judge.printSortedList();
    }
}