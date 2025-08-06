// Speech recognition functionality for voice input

$(document).ready(function () {
    // Check if browser supports the Web Speech API
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        $('.voice-input').prop('disabled', true).attr('title', 'Speech recognition not supported in this browser');
        return;
    }

    // Initialize speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US'; // Default language

    // Handle voice input button click
    $('.voice').click(function () {
        const targetId = $(this).prev('input, select').attr('id');
        const targetElement = document.getElementById(targetId);

        // Change button appearance to indicate listening
        $(this).addClass('btn-danger').removeClass('btn-secondary');
        $(this).html('Listening...');

        // Start recognition
        recognition.start();

        // Set the target element for the recognition result
        recognition.targetElement = targetElement;
        recognition.targetButton = this;
    });

    // Handle recognition result
    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        const targetElement = this.targetElement;

        // Handle different input types
        if (targetElement.tagName === 'SELECT') {
            // For select elements, try to find an option that matches the transcript
            const options = targetElement.options;
            for (let i = 0; i < options.length; i++) {
                const optionText = options[i].text.toLowerCase();
                if (optionText.includes(transcript.toLowerCase())) {
                    targetElement.selectedIndex = i;
                    $(targetElement).trigger('change');
                    break;
                }
            }
        } else if (targetElement.type === 'date') {
            // For date inputs, try to parse the date from the transcript
            try {
                const date = new Date(transcript);
                if (!isNaN(date.getTime())) {
                    targetElement.value = formatDateForInput(date);
                    $(targetElement).trigger('change');
                }
            } catch (e) {
                console.error('Could not parse date from speech input:', e);
            }
        } else if (targetElement.type === 'number') {
            // For number inputs, extract numbers from the transcript
            const numbers = transcript.match(/\d+/g);
            if (numbers && numbers.length > 0) {
                targetElement.value = numbers[0];
                $(targetElement).trigger('change');
            }
        } else {
            // For text inputs
            targetElement.value = transcript;
            $(targetElement).trigger('change');
        }
    };

    // Handle recognition end
    recognition.onend = function () {
        // Reset button appearance
        $(this.targetButton).removeClass('btn-danger').addClass('btn-secondary');
        $(this.targetButton).html('Voice');
    };

    // Handle recognition errors
    recognition.onerror = function (event) {
        console.error('Speech recognition error:', event.error);

        // Reset button appearance
        $(this.targetButton).removeClass('btn-danger').addClass('btn-secondary');
        $(this.targetButton).html('Voice');

        // Show error message
        if (event.error === 'no-speech') {
            alert('No speech was detected. Please try again.');
        } else if (event.error === 'audio-capture') {
            alert('No microphone was found. Ensure that a microphone is installed.');
        } else if (event.error === 'not-allowed') {
            alert('Permission to use microphone was denied.');
        } else {
            alert('An error occurred with the speech recognition.');
        }
    };
});
