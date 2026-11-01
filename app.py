// --- MAIN BOT LOGIC ---

// Default language
let currentLang = "english"; 

// 1. Language Toggle Function (Employee jab bhasha badle)
function setLanguage(lang) {
    currentLang = lang.toLowerCase();
    
    // Bot ka confirmation message
    let confirmMsg = currentLang === "english" 
        ? "Language set to English! You can use the menu or type below." 
        : "Bhasha Hindi set kar di gayi hai! Aap menu ka use kar sakte hain ya niche type kar sakte hain.";
    
    appendBotMessage(confirmMsg);
    
    // Language badalte hi menu ko nayi language ke questions ke sath refresh karein
    loadMenu(); 
}

// 2. Direct Chat & Keyword Search Function (For typing "scam", etc.)
function getBotResponse(userInput) {
    let searchText = userInput.toLowerCase().trim();

    if (!botResponsesDB || Object.keys(botResponsesDB).length === 0) {
        return currentLang === "english" ? "Database is loading..." : "Database load ho raha hai...";
    }

    // Step A: Exact question match
    if (botResponsesDB[userInput]) {
        return botResponsesDB[userInput][currentLang];
    }

    // Step B: Keyword Match (Agar employee sirf "scam", "budget", ya "block" likhe)
    for (let key in botResponsesDB) {
        let questionData = botResponsesDB[key];
        
        // Check agar keyword main key mein hai, ya english/hindi question mein hai
        let searchArea = key.toLowerCase();
        if (questionData.question_english) searchArea += " " + questionData.question_english.toLowerCase();
        
        if (searchArea.includes(searchText)) {
            return questionData[currentLang]; // Seedha direct jawab dega
        }
    }

    // Step C: Agar match na mile
    return currentLang === "english" 
        ? "I couldn't find an exact answer. Please try checking the training modules or rephrase your question." 
        : "Mujhe iska jawab nahi mila. Kripya menu check karein ya sawal thoda badal kar likhein.";
}

// 3. Menu Generate Function (Language ke hisaab se questions dikhane ke liye)
function loadMenu() {
    const menuContainer = document.getElementById("menu-container"); // Apne menu div ka ID daalein
    if (!menuContainer) return;
    
    let menuHTML = "";
    
    for (let key in botResponsesDB) {
        let item = botResponsesDB[key];
        
        // Agar naya structure hai (English aur Hindi questions alag), toh current language ke hisaab se sawal uthaye
        let displayQuestion = key; // Default purana Hinglish key
        
        if (item.question_english && item.question_hindi) {
            displayQuestion = currentLang === "english" ? item.question_english : item.question_hindi;
        }
        
        menuHTML += `<button class="menu-btn" onclick="sendToChat('${key}')">${displayQuestion}</button>`;
    }
    
    menuContainer.innerHTML = menuHTML;
}

// Dummy function message UI mein dikhane ke liye (Aap apne existing function se replace karein)
function appendBotMessage(msg) {
    console.log("Bot:", msg); // Yahan apni UI append line daalein
}