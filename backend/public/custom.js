// Scroll-Kontrolle für Chainlit
window.addEventListener('DOMContentLoaded', function() {
    let userScrolledUp = false;
    let isStreaming = false;
    
    // Erkennt, wenn Benutzer nach oben scrollt
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        
        // Prüft ob Benutzer nicht am Ende der Seite ist
        if (scrollTop + windowHeight < documentHeight - 50) {
            userScrolledUp = true;
        } else {
            userScrolledUp = false;
        }
    });
    
    // Beobachtet neue Nachrichten und Streaming-Updates
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // Nur scrollen wenn Benutzer nicht nach oben gescrollt hat
                if (!userScrolledUp) {
                    setTimeout(() => {
                        window.scrollTo({
                            top: document.body.scrollHeight,
                            behavior: 'smooth'
                        });
                    }, 100);
                }
            }
            
            // Beobachtet auch Textänderungen (für Streaming)
            if (mutation.type === 'characterData' || mutation.type === 'childList') {
                if (!userScrolledUp) {
                    setTimeout(() => {
                        window.scrollTo({
                            top: document.body.scrollHeight,
                            behavior: 'smooth'
                        });
                    }, 50);
                }
            }
        });
    });
    
    // Wartet bis Chainlit vollständig geladen ist
    function startObserving() {
        // Sucht nach verschiedenen möglichen Chainlit-Container
        const possibleSelectors = [
            '[data-testid="chat-messages"]',
            '.messages-container',
            '[class*="message"]',
            '[class*="chat"]',
            'main',
            '#root'
        ];
        
        let chatContainer = null;
        for (const selector of possibleSelectors) {
            chatContainer = document.querySelector(selector);
            if (chatContainer) break;
        }
        
        // Fallback auf body wenn kein spezifischer Container gefunden wird
        if (!chatContainer) {
            chatContainer = document.body;
        }
        
        console.log('Observing container:', chatContainer);
        
        observer.observe(chatContainer, {
            childList: true,
            subtree: true,
            characterData: true
        });
    }
    
    // Startet Beobachtung nach kurzer Verzögerung
    setTimeout(startObserving, 1000);
});