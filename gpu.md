---
layout: page
title: GPU Usage Report
permalink: /gpu/
---

<div class="gpu-report">
  <p>GPU utilization and memory usage for the last 90 days.</p>

  {% if site.data.gpu.servers %}
    {% for server_entry in site.data.gpu.servers %}
      {% assign server_name = server_entry[0] %}
      {% assign server = server_entry[1] %}
      
      <h2 id="{{ server_name }}">{{ server_name | capitalize }}</h2>
      
      {% if server.gpus and server.gpus.size > 0 %}
        {% for gpu_entry in server.gpus %}
          {% assign gpu_id = gpu_entry[0] %}
          {% assign gpu = gpu_entry[1] %}
          
          <h3>GPU {{ gpu_id }}</h3>
          
          <ul>
            <li><strong>Status:</strong> {% if gpu.active %}Active{% else %}Inactive{% endif %}</li>
            <li><strong>Memory Limit:</strong> {{ gpu.memory_limit }} MB</li>
          </ul>
          
          {% if gpu.metrics %}
            {% if gpu.metrics.utilization %}
              <h4>Utilization (%)</h4>
              <div class="metrics-summary">
                <p>{{ gpu.metrics.utilization.size }} data points over the last 90 days</p>
                <details>
                  <summary>View Data</summary>
                  <table>
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Avg Utilization (%)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {% for point in gpu.metrics.utilization limit:30 %}
                        <tr>
                          <td>{{ point.date }}</td>
                          <td>{{ point.value | round: 2 }}</td>
                        </tr>
                      {% endfor %}
                      {% if gpu.metrics.utilization.size > 30 %}
                        <tr>
                          <td colspan="2"><em>... and {{ gpu.metrics.utilization.size | minus: 30 }} more days</em></td>
                        </tr>
                      {% endif %}
                    </tbody>
                  </table>
                </details>
              </div>
            {% endif %}
            
            {% if gpu.metrics.memory %}
              <h4>Memory Usage (MB)</h4>
              <div class="metrics-summary">
                <p>{{ gpu.metrics.memory.size }} data points over the last 90 days</p>
                <details>
                  <summary>View Data</summary>
                  <table>
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Avg Memory (MB)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {% for point in gpu.metrics.memory limit:30 %}
                        <tr>
                          <td>{{ point.date }}</td>
                          <td>{{ point.value | round: 0 }}</td>
                        </tr>
                      {% endfor %}
                      {% if gpu.metrics.memory.size > 30 %}
                        <tr>
                          <td colspan="2"><em>... and {{ gpu.metrics.memory.size | minus: 30 }} more days</em></td>
                        </tr>
                      {% endif %}
                    </tbody>
                  </table>
                </details>
              </div>
            {% endif %}
          {% else %}
            <p><em>No metrics available</em></p>
          {% endif %}
        {% endfor %}
      {% else %}
        <p><em>No GPU data available</em></p>
      {% endif %}
    {% endfor %}
  {% else %}
    <p><em>No GPU data available. Please run data generation.</em></p>
  {% endif %}
</div>

<style>
  .gpu-report table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 20px 0;
  }
  .gpu-report th,
  .gpu-report td {
    padding: 8px 12px;
    text-align: left;
    border: 1px solid #ddd;
  }
  .gpu-report th {
    background-color: #0b3d91;
    color: white;
    font-weight: bold;
  }
  .gpu-report tr:nth-child(even) {
    background-color: #f9f9f9;
  }
  .gpu-report details {
    margin: 10px 0;
  }
  .gpu-report summary {
    cursor: pointer;
    color: #0b3d91;
    font-weight: bold;
  }
  .metrics-summary {
    background-color: #f5f5f5;
    padding: 15px;
    margin: 10px 0;
    border-left: 4px solid #0b3d91;
  }
</style>
