// CaveGen.CaveGenを以下で置き換える

public CaveGen() {
    caveGenInit();

    HashMap<String, Integer> counter = new HashMap<>();

    for (int i = 0; i < numToGenerate; i++) {
        caveGenStep(i);
        
        String key;
        if(specialCaveInfoName.equals("FC") && sublevel == 7){
            boolean oogane = false;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("Wealthy")){
                    oogane = true;
                }
            }
            key = "{oogane: " + oogane + "}";
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
        else if(specialCaveInfoName.equals("CH2") && sublevel == 2){
            int mitites = 0;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("TamagoMushi")){
                    mitites++;
                }
            }
            key = "{mitites: " + mitites + "}";
        }
        else if(specialCaveInfoName.equals("CH8") && sublevel == 1){
            int kocha = 0;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("Kochappy")){
                    kocha++;
                }
            }
            key = "{kocha: " + kocha + "}";
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
        }
        else if(specialCaveInfoName.equals("CH29") && sublevel == 1){
            int eggs = 0;
            for(Teki teki : placedTekis){
                if(teki.tekiName.equals("Egg")){
                    eggs++;
                }
            }
            key = "{eggs: " + eggs + "}";
        }
        else{
            throw new UnsupportedOperationException(specialCaveInfoName);
        }
        counter.put(key, counter.getOrDefault(key, 0) + 1);
    }

    String result = String.format("{\"seed\": 0x%08x, \"num\": 0x%08x, \"result\": {", firstGenSeed, numToGenerate);
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