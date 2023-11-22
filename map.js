var socket = io('http://localhost:8081/tracking');

// Função de inicialização do mapa
function initMap() {
    // Crie um mapa centrado nas coordenadas fornecidas
    var map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: -22.161327510050672, lng: -49.94313713397682 },
        zoom: 15 // Ajuste o nível de zoom conforme necessário
    });

    // Lidar com a atualização de localização recebida do WebSocket
    socket.on('location_update', function (data) {
        var deviceCode = document.getElementById('deviceCode').value;
        console.log('Nova Localização:', data);

        if(data.device_code === deviceCode){
            // Atualizar as coordenadas do marcador no mapa
            var map = new google.maps.Map(document.getElementById('map'), {
                center: { lat: data.latitude, lng: data.longitude },
                zoom: 15
            });

            var marker = new google.maps.Marker({
                position: { lat: data.latitude, lng: data.longitude },
                map: map,
                title: 'Localização do Dispositivo'
            });
        }
    });
}

// Função para buscar localização
function buscarLocalizacao() {
    // Obtenha os valores dos campos
    var deviceCode = document.getElementById('deviceCode').value;
    var toDate = document.getElementById('toDate').value;

    // Construa a URL com os parâmetros
    var url = `http://localhost:8081/get_location?device_code=${deviceCode}&to_date=${toDate}`;

    // Faça a solicitação AJAX usando jQuery
    $.ajax({
        url: url,
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            // Use os dados de localização retornados
            console.log('Localização:', data);
            if (Array.isArray(data.location_data) && data.location_data.length > 0) {
                let location = data.location_data[0]
                // Aqui você pode manipular os dados para exibir no mapa
                // Por exemplo, atualizando as coordenadas do marcador no mapa
                var map = new google.maps.Map(document.getElementById('map'), {
                    center: { lat: location.latitude, lng: location.longitude },
                    zoom: 15
                });

                var marker = new google.maps.Marker({
                    position: { lat: location.latitude, lng: location.longitude },
                    map: map,
                    title: 'Localização do Dispositivo'
                });
            }
        },
        error: function (xhr, status, error) {
            // Imprima informações específicas do erro
            console.error('XHR Status:', status);
            console.error('XHR Error:', error);
        }
    });

    // Faça alguma coisa com esses valores, por exemplo, chame a API de rastreio
    console.log('ID do Dispositivo:', deviceCode);
    console.log('Data de Término:', toDate);
}

    