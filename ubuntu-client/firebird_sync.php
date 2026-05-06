<?php

$base_url = "http://25.72.70.22:8000";

function fetchEndpoint($url) {
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    $json = curl_exec($ch);
    $error = curl_error($ch);
    curl_close($ch);

    if ($error) {
        return ['error' => $error];
    }

    return json_decode($json, true);
}

$articulos = fetchEndpoint("$base_url/articulos");
$stock     = fetchEndpoint("$base_url/stock");
$price     = fetchEndpoint("$base_url/price");

header('Content-Type: application/json');
echo json_encode([
    'articulos' => $articulos,
    'stock'     => $stock,
    'price'     => $price,
], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
