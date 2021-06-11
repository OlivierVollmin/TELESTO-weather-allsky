<?php

function DisplayLiveWeather(){

    // Run RainPHP.py script to read rain sensor
    $outputString = exec('/usr/bin/python3 /home/pi/weather/RainPHP.py');
    // Convert string to bool
    $bool = filter_var($outputString, FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE);

    // Display right image depending on RainPHP.py return
    $src = $bool ? '../rain.png': '../sun.png';

    ?>

<style>
/* Three image containers (use 25% for four, and 50% for two, etc) */
.column {
  float: left;
  width: 33.33%;
  padding: 5px;
}

/* Clear floats after image containers */
.row::after {
  content: "";
  clear: both;
  display: table;
}
.center {
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;
}

</style>

    <br>
    <div style="font-size : 30px"> Weather measures of the last 12 hours </div>
    <br>
    <div style="font-size : 20px"> Is the capacitif rain sensor currently dry :    <img src="<?php echo $src ?>" width="50" height="50" /> </div>

    <div class="row">
        <div class="column">
            <img style="width:100%"  class="center" src="../weather_plot.png">
        </div>
        <div class="column">
            <img style="width: 78%"  class="center"  src="../windrose.png">
        </div>
        <div class="column">
            <img style="width:100%"  class="center" src="../rainfall.png">
        </div>
    </div>

    <br>
    <div style="font-size : 15px"> Latest WEATHER_MEASUREMENT database entries </div>
    <?php

    echo "<table style='border: solid 1px black;'>";
    echo "<tr><th>ID</th><th>Temperature [°C]</th><th>Rel. pressure [hPa]</th><th>Relative humidity [%]</th><th>Wind direction</th><th>Logged</th><th>Avg wind speed [m/s]</th><th>Max wind gust [m/s]</th><th>Rainfall [mm]</th><th>Dew point temp. [°C]</th><th>Is it raining</th></tr>";

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
        $stmt = $pdo->prepare("SELECT * FROM WEATHER_MEASUREMENT ORDER BY ID DESC LIMIT 144");
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

  <?php 
}
?>
