$(document).ready(function() {
    let currentImageIndex = 0;
    let imageList = [];
    let score = {
        correctMatrix: 0,
        correctUpscale: 0,
        incorrectMatrix: 0,
        incorrectUpscale: 0,
    };

    $('#classify-button').on('click', function() {
        const model = $('#model').val();
        const directory = $('#directory').val();

        $.ajax({
            url: '/classify',
            method: 'POST',
            data: { model: model, directory: directory },
            success: function(data) {
                imageList = data.images;
                currentImageIndex = 0;
                score = {
                    correctMatrix: 0,
                    correctUpscale: 0,
                    incorrectMatrix: 0,
                    incorrectUpscale: 0,
                };
                showImage();
            }
        });
    });

    function showImage() {
        if(currentImageIndex < imageList.length) {
            const currentImage = imageList[currentImageIndex];
            $('#result-image').attr('src', currentImage.path);
            $('#result-label').text('Classification: ' + currentImage.classification);
        } else {
            alert('No more images to classify.');
        }
    }
    

    $('#matrix-button').on('click', function() {
        const classification = $('#result-label').text().split(': ')[1];
        if(classification === 'Matrix') {
            score.correctMatrix += 1;
        } else {
            score.incorrectMatrix += 1;
        }
        currentImageIndex += 1;
        showImage();
        updateScore();
    });

    $('#upscale-button').on('click', function() {
        const classification = $('#result-label').text().split(': ')[1];
        if(classification === 'Upscale') {
            score.correctUpscale += 1;
        } else {
            score.incorrectUpscale += 1;
        }
        currentImageIndex += 1;
        showImage();
        updateScore();
    });

    function updateScore() {
        $('#score-value').text('Matrix Correct: ' + score.correctMatrix + ', Upscale Correct: ' + score.correctUpscale + ', Matrix Incorrect: ' + score.incorrectMatrix + ', Upscale Incorrect: ' + score.incorrectUpscale);
    }
});
