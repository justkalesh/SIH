document.addEventListener('DOMContentLoaded', function() {
    const progressBar = document.getElementById('progress-bar');
    const quizButton = document.getElementById('quiz-button');
    let lessonCompleted = false;
    
    // Function to update progress bar
    function updateProgressBar() {
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollPercent = (scrollTop / (documentHeight - windowHeight)) * 100;
        
        progressBar.style.width = scrollPercent + '%';
        
        // Check if user has scrolled to bottom (within 50px)
        if (scrollTop + windowHeight >= documentHeight - 50 && !lessonCompleted) {
            completeLesson();
        }
    }
    
    // Function to complete lesson
    function completeLesson() {
        lessonCompleted = true;
        
        // Send request to server to mark lesson as completed
        fetch(`/complete_lesson/${LESSON_ID}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token() }}'  // You'll need to implement CSRF protection
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message
                alert(data.message);
                
                // Update XP display
                document.getElementById('user-xp').textContent = data.xp;
                
                // Show quiz button
                quizButton.style.display = 'block';
                
                // Add click handler to quiz button
                quizButton.addEventListener('click', function() {
                    window.location.href = `/quiz/${LESSON_ID}`;
                });
                
                // Add confetti effect (optional)
                createConfetti();
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    }
    
    // Simple confetti effect
    function createConfetti() {
        const colors = ['#4CAF50', '#8BC34A', '#CDDC39', '#FFC107', '#FF9800'];
        const container = document.querySelector('.lesson-container');
        
        for (let i = 0; i < 20; i++) {
            const confetti = document.createElement('div');
            confetti.style.position = 'absolute';
            confetti.style.width = '10px';
            confetti.style.height = '10px';
            confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.borderRadius = '50%';
            confetti.style.top = '50%';
            confetti.style.left = '50%';
            confetti.style.opacity = '0';
            confetti.style.transform = 'translate(-50%, -50%)';
            confetti.style.transition = 'all 2s ease-out';
            
            container.appendChild(confetti);
            
            // Simple animation using CSS transitions
            setTimeout(() => {
                confetti.style.opacity = '1';
                confetti.style.transform = `translate(${Math.random() * 400 - 200}px, ${Math.random() * 400 - 200}px)`;
                confetti.style.scale = '1';
            }, 10);
            
            // Remove after animation
            setTimeout(() => {
                confetti.remove();
            }, 2000);
        }
    }
    
    // Add scroll event listener
    window.addEventListener('scroll', updateProgressBar);
    
    // Initial progress bar update
    updateProgressBar();
});