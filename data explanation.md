📦 InternData.pkl – File Structure and Contents
The InternData.pkl file is a serialized Python dictionary containing four main components:
•	'mep_data'
•	'ssep_upper_data'
•	'ssep_lower_data'
•	'_surgerydata'
Each of the first three keys (mep_data, ssep_upper_data, ssep_lower_data) maps to a pandas DataFrame containing electrophysiological monitoring , collected during surgeries.
🔍 DataFrame Structure
Each DataFrame contains the following columns:
Column	Description
surgery_id	Unique identifier for the surgery this data belongs to
timestamp	Time of signal capture (in seconds)
channel	Electrode channel pair used for the recording (e.g., LDI1-LDI2)
values	A list of raw signal amplitudes collected at the given timestamp
stimulus	Stimulus parameters applied during signal recording (usually a dictionary)
signal_rate	Sampling rate of the signal (e.g., 10,000 Hz)
baseline_timestamp	Time at which baseline data was collected
baseline_values	List of signal amplitudes recorded during the baseline (pre-stimulus) period
baseline_stimulus	Stimulus parameters used for the baseline
baseline_signal_rate	Sampling rate used during baseline recording
These DataFrames contain multiple rows per timestamp and channel, allowing detailed temporal resolution for neurophysiological analysis.
🏥 _surgerydata
This key contains metadata for each surgery, stored as a dictionary. For each surgery_id, you can find:
•	Date of the surgery
•	Protocol used during the procedure

