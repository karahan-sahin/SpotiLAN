var previousBtn = document.getElementById('previous-btn');
var playBtn = document.getElementById('play-btn');
var pauseBtn = document.getElementById('pause-btn');
var nextBtn = document.getElementById('next-btn');
var searchBtn = document.getElementById('search-btn');

// Function to update the song list
function updateSongList() {
    fetch('/api/song-list')
        .then(function (response) {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Request failed.');
        })
        .then(function (data) {
            var songListContainer = document.getElementById('song-list-container');
            songListContainer.innerHTML = '';

            data.song_list.forEach(function (song) {
                var songCard = `
                        <div class="col-md-12 mb-4" style="padding-top: 5px">
                            <div class="card h-100 rounded p-3">
                                <div class="card-body">
                                    <h5 class="card-title">${song}</h5>
                                </div>
                            </div>
                        </div>
                    `;
                songListContainer.innerHTML += songCard;
            });
        })
        .catch(function (error) {
            console.log(error);
            // Handle error if needed
        });
}

// Function to update the host list
function updateHostList() {
    fetch('/api/host-list')
        .then(function (response) {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Request failed.');
        })
        .then(function (data) {
            var hostListContainer = document.getElementById('host-list');
            hostListContainer.innerHTML = '';

            data.host_list.forEach(function (host) {
                var hostItem = document.createElement('li');
                hostItem.className = 'list-group-item';
                hostItem.textContent = host;
                hostListContainer.appendChild(hostItem);
            });
        })
        .catch(function (error) {
            console.log(error);
            // Handle error if needed
        });
}

// Initialize
updateSongList();
updateHostList();

// Update every 5 seconds
setInterval(updateSongList, 5000);
setInterval(updateHostList, 5000);

previousBtn.addEventListener('click', function () {
    sendRequest('previous');
});
playBtn.addEventListener('click', function () {
    sendRequest('play');
});

pauseBtn.addEventListener('click', function () {
    sendRequest('pause');
});

nextBtn.addEventListener('click', function () {
    sendRequest('next');
});

function sendRequest(action) {
    fetch('http://127.0.0.1:5000/api/audio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({action: action})
    })
        .then(function (response) {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Request failed.');
        })
        .then(function (data) {
            console.log(data);
            // Handle response data if needed
        })
        .catch(function (error) {
            console.log(error);
            // Handle error if needed
        });
}

searchBtn.addEventListener('click', function () {
    updateSearchResults();
});

// Function to update the search results
function updateSearchResults() {
        console.log("Sending request...");
        fetch('http://127.0.0.1:5000/api/search', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({"query": document.getElementById("search-bar")})
        })
        .then(function (response) {
            console.log(response)
            if (response.ok) {
                return response.json();
            }
            throw new Error('Request failed.');
        })
        .then(function (data) {
            var songListContainer = document.getElementById('search-results');
            songListContainer.innerHTML = '';

            data.search_results.forEach(function (song) {
                var songCard = `
                        <div class="col-md-12 mb-4" style="padding-top: 5px">
                            <div class="card h-100 rounded p-3">
                                <div class="card-body">
                                    <h5 class="card-title">${song.title}</h5>
                                </div>
                            </div>
                        </div>
                    `;
                songListContainer.innerHTML += songCard;
            });
        })
        .catch(function (error) {
            console.log(error);
            // Handle error if needed
        });
}