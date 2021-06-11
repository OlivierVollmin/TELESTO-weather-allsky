<?php
// Database settings
$db = "cpu_tempDB";
$dbhost = "localhost";
$dbport = 3306;
$dbuser = "pi";
$dbpasswd = "TELESTO";

//Try Statement
try {
    //Creating a New PDO Connection
    $pdo = new PDO('mysql:host=' . $dbhost . ';port=' . $dbport . ';dbname=' . $db . '', $dbuser,  $dbpasswd);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    //mysql Select * from table
    $stmt = $pdo->prepare("select * from CPU_TEMP_TABLE where CREATED > DATE_SUB(NOW(), INTERVAL 14 DAY) order by ID DESC");
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
