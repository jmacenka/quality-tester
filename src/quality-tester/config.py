# Configuration File for default parameters
default_config = {
    'success_rate': 90, # Successrate in %
    'company_name': 'ROI-EFESO', # Company name
    'min_wait_time': 10000, # Minimum duration in milliseconds for Test-simulation
    'max_wait_time': 5000,  # Maximum duration in milliseconds for Test-simulation
    'default_user': 'pi', # Default user, needs to be pi, if you want to use a different user some adaptions to the implementation are required
    'logo_name': 'logo.png', # Name of the logo to be used
    'password': 'updateplease', # Default password can be manually change in src/quality-tester/static/configuration/config.yaml
    'simulate_pictures':False, # Disable the real scan for picture and always just return a simulated result
}
target_pics_folder = 'static/target_pics'
config_folder = 'static/configuration'
logo_folder = 'static/img'