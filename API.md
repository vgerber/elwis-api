Sehr geehrter Herr Gerber,

herzlichen Dank für Ihre E-Mail, die wir Ihnen gerne wie folgt beantworten.

Zur Abfrage von ELWIS-Daten können Sie einen standardisierten SOAP-XML-Webservice (Notices-to-Skippers 4.0) nutzen, über den Wasserstände und Nachrichten für die Binnenschifffahrt (NfB) abgerufen werden können.

Ein Zugang zum SOAP-XML-Webservice wird über folgende URL angeboten: https://nts40.elwis.de/server/web/MessageServer.php?wsdl.

Die Dokumentation im Rahmen des EU-Projekts RIS/CESNI kann über nachfolgende Seite aufgerufen werden: https://ris.cesni.eu/332-en.html.

Weiterführende Informationen auch anderer europäischer Länder können über das EuRIS-Portal eingesehen und auch abgerufen werden: https://www.eurisportal.eu/service/api/intro?KL=de.

Der ELWIS-NTS40-Webservice benötigt keine Authentifizierung. Diese Information kann im „Header“ freigelassen werden.

Eine direkte Abfrage einer bestimmten NfB-ID ist leider aktuell nicht möglich.

Aktuelle Nachrichten für die Binnenschifffahrt (NfB) können Sie wie folgt über den Gültigkeitszeitraum bewerkstelligen:

```
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.ris.eu/nts.ms/2.0.4.0" xmlns:ns1="http://www.ris.eu/nts/4.0.4.0">
   <soapenv:Header/>
   <soapenv:Body>
      <ns:get_messages_query>
         <ns:message_type>FTM</ns:message_type>

         <ns:validity_period>
            <ns1:date_start>2024-05-01</ns1:date_start>

            <ns1:date_end>2024-05-31</ns1:date_end>
         </ns:validity_period>

         <ns:paging_request>
            <ns:offset>0</ns:offset>
            <ns:limit>100</ns:limit>
            <ns:total_count>true</ns:total_count>
         </ns:paging_request>
      </ns:get_messages_query>
   </soapenv:Body>
</soapenv:Envelope>
```

Diese Abfrage kann mit geeigneten Mitteln automatisiert werden. Für den manuellen Abruf kann z. B. das Werkzeug "SOAP-UI" genutzt werden.
