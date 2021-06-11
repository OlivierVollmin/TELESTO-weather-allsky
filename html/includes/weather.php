<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RPi Weather Station</title>
    <style>
        h1 {
            text-align: center;
        }

        p {
            text-align: center;
        }

        div {
            text-align: left;
        }

        div.a {
            font-size: 250%;
        }
    </style>
</head>

<body>
    <div><A HREF="http://192.168.1.111">Back to the menu</A> </div>


    <figure class="half" style="display:flex">
        <img width="560" height="420" src="../weather_plot.png">
        <img width="500" height="500" src="../windrose.png">
        <img width="560" height="420" src="../rainfall.png">
    </figure>


    <?php
    // Run RainPHP.py script to read rain sensor
    $outputString = exec('/usr/bin/python3 /home/pi/weather/RainPHP.py');
    // Convert string to bool
    $bool = filter_var($outputString, FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE);

    // Display right image depending on RainPHP.py return
    $src = $bool ? '../rain.png': '../sun.png';
    ?>

    <div class="a"> Is it currently raining : <img src="<?php echo $src ?>" width="40" height="40" /> </div>

    <?php

    echo "<table style='border: solid 1px black;'>";
    echo "<tr><th>ID</th><th>AMBIENT_TEMPERATURE</th><th>AIR_PRESSURE</th><th>HUMIDITY</th><th>WIND_DIRECTION</th><th>CREATED</th><th>WIND_SPEED</th><th>WIND_GUST_SPEED</th><th>RAINFALL</th><th>DEW_POINT_TEMPERATURE</th><th>IS_RAINING</th></tr>";

    class TableRows extends RecursiveIteratorIterator
    {
        function __construct($it)
        {
            parent::__construct($it, self::LEAVES_ONLY);
        }

        function current()
        {
            return "<td style='width:150px;border:1px solid black;'>" . parent::current() . "</td>";
        }

        function beginChildren()
        {
            echo "<tr>";
        }

        function endChildren()
        {
            echo "</tr>" . "\n";
        }
    }

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
        $stmt = $pdo->prepare("SELECT * FROM WEATHER_MEASUREMENT ORDER BY ID DESC LIMIT 10");
        $stmt->execute();

        // set the resulting array
        $result = $stmt->setFetchMode(PDO::FETCH_ASSOC);
        foreach (new TableRows(new RecursiveArrayIterator($stmt->fetchAll())) as $k => $v) {
            echo $v;
        }
    } catch (PDOException $e) {
        echo "Error: " . $e->getMessage();
    }

    $pdo = null;
    echo "</table>";
    ?>

</body>

</html>
