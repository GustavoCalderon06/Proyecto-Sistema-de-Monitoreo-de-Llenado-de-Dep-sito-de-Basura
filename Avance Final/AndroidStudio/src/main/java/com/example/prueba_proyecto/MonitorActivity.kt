package com.example.prueba_proyecto

import androidx.appcompat.app.AppCompatActivity
import android.os.AsyncTask
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.*
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.Date

class MonitorActivity : AppCompatActivity() {

    private lateinit var tvNivel: TextView
    private lateinit var listViewHistorial: ListView
    private lateinit var historialAdapter: ArrayAdapter<String>
    private lateinit var tvUltimaActualizacion: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_monitor)

        val btnConsultar: Button = findViewById(R.id.btnConsultar)
        tvNivel = findViewById(R.id.tvNivel)
        listViewHistorial = findViewById(R.id.listViewHistorial)

        tvUltimaActualizacion = findViewById(R.id.tvUltimaActualizacion)

        historialAdapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, ArrayList())
        listViewHistorial.adapter = historialAdapter

        btnConsultar.setOnClickListener {
            ConsultarNivelTask().execute()
        }
    }

    private inner class ConsultarNivelTask : AsyncTask<Void, Void, String>() {
        override fun doInBackground(vararg params: Void?): String? {
            return try {
                val url = URL("http://52.200.139.211:5000/api/last_data")
                val urlConnection = url.openConnection() as HttpURLConnection
                try {
                    val bufferedReader = BufferedReader(InputStreamReader(urlConnection.inputStream))
                    val stringBuilder = StringBuilder()
                    var line: String?
                    while (bufferedReader.readLine().also { line = it } != null) {
                        stringBuilder.append(line).append("\n")
                    }
                    bufferedReader.close()
                    stringBuilder.toString()
                } finally {
                    urlConnection.disconnect()
                }
            } catch (e: Exception) {
                Log.e("MonitorActivity", "Error fetching data", e)
                null
            }
        }

        override fun onPostExecute(response: String?) {
            response?.let {
                try {
                    val jsonObject = JSONObject(it)
                    val nivelLlenado = jsonObject.getDouble("nivelLlenado")

                    val currentDate = Date()
                    val dateTimeFormatter = SimpleDateFormat("dd/MM/yyyy HH:mm:ss")
                    val timeFormatter = SimpleDateFormat("HH:mm:ss")
                    val formattedDateTime = dateTimeFormatter.format(currentDate)
                    val formattedTime = timeFormatter.format(currentDate)

                    tvUltimaActualizacion.text = "Última actualización: $formattedDateTime"

                    val historialText = "Nivel de Llenado: $nivelLlenado% a las $formattedTime"

                    if (nivelLlenado > 80.0) {
                        historialAdapter.clear()
                        tvNivel.text = "Nivel de Llenado: $nivelLlenado%"
                        historialAdapter.add(historialText)
                    } else if (nivelLlenado == 0.0) {
                        if (historialAdapter.isEmpty() || historialAdapter.getItem(0) != historialText) {
                            historialAdapter.clear()
                            historialAdapter.add(historialText)
                        }
                        tvNivel.text = "Nivel de Llenado: $nivelLlenado%"
                    } else {
                        if (historialAdapter.isEmpty() || historialAdapter.getItem(0) != historialText) {
                            historialAdapter.add(historialText)
                        }
                        tvNivel.text = "Nivel de Llenado: $nivelLlenado%"
                    }

                    listViewHistorial.visibility = View.VISIBLE
                } catch (e: Exception) {
                    Log.e("MonitorActivity", "Error parsing JSON", e)
                }
            } ?: run {
                Log.e("MonitorActivity", "Response is null")
            }
        }
    }
}
