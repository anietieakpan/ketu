@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Path to configuration file')
@click.option('--source', '-s', required=True,
              help='Path to video file or camera index (e.g., 0 for first camera)')
@click.option('--output', '-o', type=click.Path(),
              help='Output directory')
def detect(config, source, output):
    """Run license plate detection"""
    try:
        print(f"Starting detection with source: {source}")
        
        # Load configuration
        config_path = config or Path(__file__).parent.parent / 'config' / 'default_config.yaml'
        print(f"Using config from: {config_path}")
        
        with open(config_path) as f:
            cfg = yaml.safe_load(f)

        # Initialize components
        print("Initializing components...")
        frame_processor = FrameProcessor(min_confidence=cfg['detector']['min_confidence'])
        visualizer = DetectionVisualizer(cfg)
        tracker = DetectionTracker(max_persistence=cfg['detector']['detection_persistence'])
        storage = SQLiteStorage(cfg['storage']['path'])
        
        # Create detector
        detector = LicensePlateDetector(
            config=cfg,
            frame_processor=frame_processor,
            visualizer=visualizer,
            tracker=tracker,
            storage=storage
        )
        
        # Run detection
        print(f"Opening video source: {source}")
        if str(source).isdigit():
            print("Processing camera feed...")
            _process_camera(detector, int(source))
        elif Path(source).exists():
            print("Processing video file...")
            _process_video(detector, str(source))
        else:
            raise click.ClickException(f"Invalid source: {source}")
            
    except Exception as e:
        print(f"Error in detection: {str(e)}")
        raise click.ClickException(str(e))