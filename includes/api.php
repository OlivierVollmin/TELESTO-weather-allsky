<?php
// Database settings
$db = "weatherDB";
$dbhost = "localhost";
$dbport = 3306;
$dbuser = "pi";
$dbpasswd = "TELESTO";

//Try Statement
try {
    //Creating a New PDO Connection
    $pdo = new PDO('mysql:host=' . $dbhost . ';port=' . $dbport . ';dbname=' . $db . '', $dbuser, $dbpasswd);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    //mysql Select * from table
    $stmt = $pdo->prepare("SELECT * FROM WEATHER_MEASUREMENT ORDER BY ID DESC LIMIT 1440");
    $stmt->execute();

    //Fetch data
    $data = $stmt->fetchAll(PDO::FETCH_ASSOC);

    //Close cursor
    $stmt->closeCursor();
    
    //Set header type to json
    header("content-type:application/json");

    //Echo json encoded array
    echo json_encode($data);

} catch (PDOException $e) {
    echo "Error: " . $e->getMessage();
    die;
}
?>
