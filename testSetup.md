To create a setup for testing the tool do the following
1. Setup and download MySQL, Apache and PHP
   ```
   apt update && apt install mysql-server -y && mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS sample; USE sample; CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50), surname VARCHAR(50)); INSERT INTO users (name, surname) VALUES ('John', 'Doe'), ('Jane', 'Smith'), ('Alice', 'Brown');" && mysql -u root -p -e "CREATE USER IF NOT EXISTS 'sample'@'localhost' IDENTIFIED BY 'sample'; GRANT ALL PRIVILEGES ON sample.* TO 'sample'@'localhost'; FLUSH PRIVILEGES;" && apt install apache2 libapache2-mod-php php php-{cli,fpm,json,pdo,mysql,zip,gd,mbstring,curl,xml,bcmath} -y
   ```
2. Edit the /etc/mysql/my.cnf or /etc/my.cnf
   ```
   [mysqld]
   general_log_file = /var/log/mysql/mysql.log
   general_log = 1
   log-raw = 1
   ```
3. Inside /var/www/html remove index.html and put this index,php file:
   ```
   <?php
   $db_host = 'localhost';
   $db_user = 'sample';
   $db_pass = 'sample';
   $db_name = 'sample';
   
   $conn = new mysqli($db_host, $db_user, $db_pass, $db_name);
   
   if ($conn->connect_error) {
       die("Connection failed: " . $conn->connect_error);
   }
   
   $params = [
       'name1' => isset($_REQUEST['name1']) ? $_REQUEST['name1'] : null,
       'name2' => isset($_REQUEST['name2']) ? $_REQUEST['name2'] : null,
       'name3' => isset($_REQUEST['name3']) ? $_REQUEST['name3'] : null,
       'name4' => isset($_REQUEST['name4']) ? $_REQUEST['name4'] : null,
       'name5' => isset($_REQUEST['name5']) ? $_REQUEST['name5'] : null,
       'name6' => isset($_REQUEST['name6']) ? $_REQUEST['name6'] : null,
       'name7' => isset($_REQUEST['name7']) ? $_REQUEST['name7'] : null,
       'name8' => isset($_REQUEST['name8']) ? $_REQUEST['name8'] : null,
       'name9' => isset($_REQUEST['name9']) ? $_REQUEST['name9'] : null
   ];
   
   foreach ($params as $key => $value) {
       if ($value !== null) {
           switch ($key) {
               case 'name1':
                   $query = "SELECT * FROM users WHERE name = $value";
                   break;
               case 'name2':
                   $query = "SELECT * FROM users WHERE name = \"$value\"";
                   break;
               case 'name3':
                   $query = "SELECT * FROM users WHERE name = '$value'";
                   break;
               case 'name4':
                   $query = "SELECT * FROM users WHERE name = `$value`";
                   break;
               case 'name5':
                   $query = "SELECT * FROM users WHERE name = ' ( \" $value \" ) '";
                   break;
               case 'name6':
                   $query = "SELECT * FROM users WHERE name = \"'$value'\"";
                   break;
               case 'name7':
                   $query = "SELECT * FROM users WHERE name = ($value)";
                   break;
               case 'name8':
                   $query = "SELECT * FROM users WHERE name = ' ($value) '";
                   break;
               case 'name9':
                   $query = "SELECT * FROM users WHERE name = ('$value')";
                   break;
               default:
                   continue 2;
           }
   
           echo "<h3>Executing query for $key:</h3>";
           echo "<pre>$query</pre>";
   
           $result = $conn->query($query);
   
           if ($result && $result->num_rows > 0) {
               echo "<table border='1'>";
               echo "<tr>";
               while ($field_info = $result->fetch_field()) {
                   echo "<th>{$field_info->name}</th>";
               }
               echo "</tr>";
   
               while ($row = $result->fetch_assoc()) {
                   echo "<tr>";
                   foreach ($row as $col) {
                       echo "<td>$col</td>";
                   }
                   echo "</tr>";
               }
               echo "</table>";
           } else {
               echo "No results or error in query: " . $conn->error;
           }
       }
   }
   
   $conn->close();
   ?>
   ```
4. Test the tool
   ```
   python3 buraq.py -u 'http://138.201.119.180/?name6=test'
   ```
